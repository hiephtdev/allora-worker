from flask import Flask, jsonify, Response
import sqlite3
import os
import numpy as np
from gluonts.model.deepar import DeepAREstimator
from gluonts.trainer import Trainer
from gluonts.dataset.common import ListDataset
import pandas as pd
from app_config import DATABASE_PATH

# Constants
API_PORT = int(os.environ.get('API_PORT', 8000))
PREDICTION_LENGTH = int(os.environ.get('PREDICTION_LENGTH', 10))  # Prediction length from environment variable

# HTTP Response Codes
HTTP_RESPONSE_CODE_200 = 200
HTTP_RESPONSE_CODE_404 = 404
HTTP_RESPONSE_CODE_500 = 500

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health():
    return "Hello, World, I'm alive!"

@app.route('/inference/<token>', methods=['GET'])
def get_inference(token):
    if not token:
        return jsonify({"error": "Token is required"}), HTTP_RESPONSE_CODE_404
    
    token_name = f"{token}USD".lower()

    try:
        # Fetch data from the database
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT price FROM prices 
                WHERE token=?
                ORDER BY block_height ASC
            """, (token_name,))
            result = cursor.fetchall()

        if not result or len(result) == 0:
            return jsonify({"error": "No data found for the specified token"}), HTTP_RESPONSE_CODE_404

        price_data = [row[0] for row in result]
        start_time = "2024-08-01 00:00:00"  # Replace with actual start time if available

        # Prepare the dataset for GluonTS
        data = ListDataset([{"start": start_time, "target": price_data}], freq="1min")
        
        # Train a simple DeepAR model (can be pre-trained for more advanced usage)
        estimator = DeepAREstimator(freq="1min", prediction_length=PREDICTION_LENGTH, trainer=Trainer(epochs=5))
        predictor = estimator.train(data)
        
        # Predict the future values
        forecast_it = predictor.predict(data)
        forecast = list(forecast_it)[0]
        
        # Extract mean forecast values
        mean_forecast = forecast.mean.tolist()

        # Return the forecasted mean values
        return Response(str(mean_forecast), status=HTTP_RESPONSE_CODE_200)

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_RESPONSE_CODE_500

@app.route('/truth/<token>/<block_height>', methods=['GET'])
def get_price(token, block_height):
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
            return jsonify({'block_height': result[0], 'price': result[1]}), HTTP_RESPONSE_CODE_200
        else:
            return jsonify({'error': 'No price data found for the specified token and block_height'}), HTTP_RESPONSE_CODE_404

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_RESPONSE_CODE_500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=API_PORT)
