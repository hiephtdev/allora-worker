from flask import Flask, jsonify, Response
import sqlite3
import os
import pandas as pd
from fbprophet import Prophet
from app_config import DATABASE_PATH

# Constants
API_PORT = int(os.environ.get('API_PORT', 8000))

# HTTP Response Codes
HTTP_RESPONSE_CODE_200 = 200
HTTP_RESPONSE_CODE_404 = 404
HTTP_RESPONSE_CODE_500 = 500

app = Flask(__name__)

# Flask routes
@app.route('/', methods=['GET'])
def health():
    return "Hello, World, I'm alive!"

@app.route('/inference/<token>', methods=['GET'])
def get_inference(token):
    if not token:
        return jsonify({"error": "Token is required"}), HTTP_RESPONSE_CODE_404
    
    token_name = f"{token}USD".lower()

    try:
        # Initialize Prophet model
        model = Prophet()
    except Exception as e:
        return jsonify({"model error": str(e)}), HTTP_RESPONSE_CODE_500
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT block_height, price FROM prices 
            WHERE token=?
            ORDER BY block_height ASC
        """, (token_name,))
        result = cursor.fetchall()

    if not result or len(result) == 0:
        return jsonify({"error": "No data found for the specified token"}), HTTP_RESPONSE_CODE_404
    
    # Prepare data for Prophet
    df = pd.DataFrame(result, columns=['ds', 'y'])  # 'ds' là cột thời gian, 'y' là giá trị

    try:
        model.fit(df)
        
        # Lấy periods từ biến môi trường và chuyển đổi thành số nguyên
        periods = int(os.environ.get('PERIODS', 10))  # Mặc định là 10 phút nếu không thiết lập
        
        # Tạo DataFrame cho khoảng thời gian cần dự đoán
        future = model.make_future_dataframe(periods=periods, freq='T')

        # Dự đoán
        forecast = model.predict(future)

        # Lấy giá trị dự đoán cuối cùng
        mean_forecast = forecast['yhat'].iloc[-1]

        # Trả kết quả
        predictions = {
            f"{periods}m_forecast": mean_forecast
        }

        print(f"{token} inference: {predictions}")
        return jsonify(predictions), HTTP_RESPONSE_CODE_200
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
