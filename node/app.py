from flask import Flask, jsonify, Response
import sqlite3
import os
import torch
from chronos import ChronosPipeline
from app_config import DATABASE_PATH

# Constants
MODEL_NAME = "amazon/chronos-t5-tiny"
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
        pipeline = ChronosPipeline.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )
    except Exception as e:
        return jsonify({"pipeline error": str(e)}), HTTP_RESPONSE_CODE_500
    
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
    
    # Lấy toàn bộ dữ liệu giá và chuyển thành tensor
    context = torch.tensor([row[0] for row in result])
    
    # Lấy prediction_length từ biến môi trường, ví dụ như 10, 20, hoặc 1440
    prediction_length = int(os.environ.get('PREDICTION_LENGTH', 10))

    try:
        forecast = pipeline.predict(context, prediction_length)
        mean_forecast = forecast[0].mean().item()
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
