from flask import Flask, jsonify, Response
import sqlite3
import os
import numpy as np
from gluonts.mx.model.deepar import DeepAREstimator
from gluonts.mx.trainer import Trainer
from gluonts.dataset.common import ListDataset
from gluonts.model.predictor import Predictor
import pandas as pd
from app_config import DATABASE_PATH
from datetime import datetime

# Constants
API_PORT = int(os.environ.get('API_PORT', 8000))
PREDICTION_LENGTH = int(os.environ.get('PREDICTION_LENGTH', 10))  # Prediction length from environment variable
MODEL_PATH = "models"  # Directory to save models

# HTTP Response Codes
HTTP_RESPONSE_CODE_200 = 200
HTTP_RESPONSE_CODE_404 = 404
HTTP_RESPONSE_CODE_500 = 500

app = Flask(__name__)

def get_or_train_model(token_name, data):
    model_filename = os.path.join(MODEL_PATH, f"{token_name}_deepar_model_{PREDICTION_LENGTH}m")
    
    if os.path.exists(model_filename):
        print(f"Loading existing model for {token_name} with prediction length {PREDICTION_LENGTH} from {model_filename}")
        predictor = Predictor.deserialize(model_filename)
    else:
        print(f"Training new model for {token_name} with prediction length {PREDICTION_LENGTH}")
        estimator = DeepAREstimator(freq="1min", prediction_length=PREDICTION_LENGTH, trainer=Trainer(epochs=5))
        predictor = estimator.train(data)
        
        os.makedirs(MODEL_PATH , exist_ok=True)
        predictor.serialize(model_filename)
    
    return predictor

@app.route('/', methods=['GET'])
def health():
    print("Health check endpoint was called.")
    return "Hello, World, I'm alive!"

@app.route('/inference/<token>', methods=['GET'])
def get_inference(token):
    print(f"{datetime.now()}: Received request for inference with token: {token}")

    if not token:
        print("No token provided in request.")
        return jsonify({"error": "Token is required"}), HTTP_RESPONSE_CODE_404
    
    token_name = f"{token}USD".lower()

    try:
        # Fetch data from the database
        print(f"Fetching price data for token: {token_name}")
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT price FROM prices 
                WHERE token=?
                ORDER BY block_height ASC
            """, (token_name,))
            result = cursor.fetchall()

        if not result or len(result) == 0:
            print(f"No data found for token: {token_name}")
            return jsonify({"error": "No data found for the specified token"}), HTTP_RESPONSE_CODE_404

        price_data = [float(row[0]) for row in result]  # Ensure prices are floats
        start_time = "2024-08-01 00:00:00"  # Replace with actual start time if available

        print(f"{datetime.now()}: {token_name} Preparing dataset for prediction. Data length: {len(price_data)}")
        # Prepare the dataset for GluonTS
        data = ListDataset([{"start": start_time, "target": price_data}], freq="1min")
        
        # Get or train the model
        predictor = get_or_train_model(token_name, data)
        
        # Predict the future values
        print(f"{datetime.now()}: {token_name} Generating predictions...")
        forecast_it = predictor.predict(data)
        forecast = list(forecast_it)[0]
        
        # Extract mean forecast values
        mean_forecast = forecast.mean.tolist()
        final_price = mean_forecast[-1]

        print(f"{datetime.now()}: {token_name} Final predicted price: {final_price}")
        # Return the final forecasted mean value
        return Response(str(final_price), status=HTTP_RESPONSE_CODE_200)

    except Exception as e:
        print(f"Error during inference: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_RESPONSE_CODE_500

@app.route('/truth/<token>/<block_height>', methods=['GET'])
def get_price(token, block_height):
    print(f"Received request for historical price with token: {token} at block height: {block_height}")

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT block_height, price 
                FROM prices 
                WHERE token=? AND block_height <= ? 
                ORDER BY ABS(block_height - ?) 
                LIMIT 1
            """, (token.lower(), block_height, block_height))
            result = cursor.fetchone()

        if result:
            print(f"Found price for block height {block_height}: {result[1]}")
            return jsonify({'block_height': result[0], 'price': result[1]}), HTTP_RESPONSE_CODE_200
        else:
            print(f"No price data found for token: {token} at block height: {block_height}")
            return jsonify({'error': 'No price data found for the specified token and block_height'}), HTTP_RESPONSE_CODE_404

    except Exception as e:
        print(f"Error fetching price data: {str(e)}")
        return jsonify({"error": str(e)}), HTTP_RESPONSE_CODE_500

if __name__ == '__main__':
    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_PATH)
    print(f"Starting server on port {API_PORT}...")
    app.run(host='0.0.0.0', port=API_PORT)
