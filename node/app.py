from flask import Flask, jsonify, Response
import sqlite3
import os
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from app_config import DATABASE_PATH

# Constants
API_PORT = int(os.environ.get('API_PORT', 8000))
LOOK_BACK = 10  # Dùng 10 phút trước đó để dự đoán
PREDICTION_STEPS = 10  # Dự đoán 10 phút tiếp theo

# HTTP Response Codes
HTTP_RESPONSE_CODE_200 = 200
HTTP_RESPONSE_CODE_404 = 404
HTTP_RESPONSE_CODE_500 = 500

app = Flask(__name__)

def create_lstm_model():
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(LOOK_BACK, 1)))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def prepare_data_for_lstm(data, look_back):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    X, Y = [], []
    for i in range(len(scaled_data) - look_back - 1):
        X.append(scaled_data[i:(i + look_back), 0])
        Y.append(scaled_data[i + look_back, 0])
    X = np.array(X)
    Y = np.array(Y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, Y, scaler

@app.route('/', methods=['GET'])
def health():
    return "Hello, World, I'm alive!"

@app.route('/inference/<token>', methods=['GET'])
def get_inference(token):
    if not token:
        return jsonify({"error": "Token is required"}), HTTP_RESPONSE_CODE_404
    
    token_name = f"{token}USD".lower()

    try:
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
        
        # Preprocess data
        prices = np.array([x[0] for x in result]).reshape(-1, 1)
        model = create_lstm_model()
        X, Y, scaler = prepare_data_for_lstm(prices, LOOK_BACK)
        
        # Train the model
        model.fit(X, Y, epochs=10, batch_size=1, verbose=2)

        # Make predictions for the next 10 minutes
        recent_data = scaler.transform(prices[-LOOK_BACK:]).reshape(1, LOOK_BACK, 1)
        predictions = []
        for _ in range(PREDICTION_STEPS):
            pred = model.predict(recent_data)
            predictions.append(pred[0][0])
            recent_data = np.append(recent_data[:, 1:, :], pred.reshape(1, 1, 1), axis=1)

        # Inverse scaling to get actual prices
        predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))

        # Get the mean forecast for the next 10 minutes
        mean_forecast = np.mean(predictions)
        print(f"{token} inference: {mean_forecast}")
        return Response(str(mean_forecast), status=HTTP_RESPONSE_CODE_200)

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_RESPONSE_CODE_500

@app.route('/truth/<token>/<block_height>', methods=['GET'])
def get_price(token, block_height):
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=API_PORT)
