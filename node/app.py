from flask import Flask, jsonify, Response
import requests
import sqlite3
from datetime import datetime, timedelta
import retrying
import os
import torch
from chronos import ChronosPipeline

# Constants
MODEL_NAME = "amazon/chronos-t5-tiny"
WORKER_TYPE = int(os.environ.get('WORKER_TYPE', 1))
CGC_API_KEY = os.environ['CGC_API_KEY']
API_PORT = int(os.environ.get('API_PORT', 8000))
ALLORA_VALIDATOR_API_URL = os.environ.get('ALLORA_VALIDATOR_API_URL', 'http://localhost:1317/')
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'prices.db')
BLOCK_TIME_SECONDS = 5

# HTTP Response Codes
HTTP_RESPONSE_CODE_200 = 200
HTTP_RESPONSE_CODE_404 = 404
HTTP_RESPONSE_CODE_500 = 500

# Endpoint for querying the latest block
URL_QUERY_LATEST_BLOCK = "cosmos/base/tendermint/v1beta1/blocks/latest"

app = Flask(__name__)

# Retry decorator for network requests
@retrying.retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def fetch_data(url):
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": CGC_API_KEY
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def check_create_table():
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prices (
                    block_height INTEGER,
                    token TEXT,
                    price REAL,
                    PRIMARY KEY (block_height, token)
                )
            ''')
        print("Prices table created successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred while creating the table: {str(e)}")

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
            ORDER BY block_height DESC
        """, (token_name,))
        result = cursor.fetchall()

    if not result:
        return jsonify({"error": "No data found for the specified token"}), HTTP_RESPONSE_CODE_404
    
    context = torch.tensor([x[0] for x in result])
    prediction_length = 1

    try:
        forecast = pipeline.predict(context, prediction_length)
        mean_forecast = forecast[0].mean().item()
        print(f"{token} inference: {mean_forecast}")
        return Response(str(mean_forecast), status=HTTP_RESPONSE_CODE_200)
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_RESPONSE_CODE_500

@app.route('/update/<token_name>/<token_from>/<token_to>', methods=['GET'])
def update_price(token_name, token_from, token_to='usd'):
    try:
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={token_from}&vs_currencies={token_to}'
        prices = fetch_data(url)

        if token_from.lower() not in prices:
            return jsonify({'error': 'Invalid token ID'}), HTTP_RESPONSE_CODE_404

        price = prices[token_from.lower()][token_to.lower()]
        block_data = get_latest_network_block()
        latest_block_height = block_data['block']['header']['height']
        token = token_name.lower()

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO prices (block_height, token, price) VALUES (?, ?, ?)", (latest_block_height, token, price))
            conn.commit()

        print(f"Inserted data point {latest_block_height} : {price}")
        return jsonify({'message': f'{token} price updated successfully'}), HTTP_RESPONSE_CODE_200
    except Exception as e:
        return jsonify({'error': f'Failed to update {token_name} price: {str(e)}'}), HTTP_RESPONSE_CODE_500

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

def init_price_token(token_name, token_from, token_to):
    try:
        check_create_table()

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM prices WHERE token=?", (token_name.lower(),))
            count = cursor.fetchone()[0]

        if count > 0:
            print(f'Data already exists for {token_name} token, {count} entries')
            return

        end_date = datetime.now()
        days = 1 if WORKER_TYPE == 1 else (90 if WORKER_TYPE == 2 else (180 if WORKER_TYPE == 3 else 1))
        start_date = end_date - timedelta(days=days)

        block_data = get_latest_network_block()
        latest_block_height = int(block_data['block']['header']['height'])

        start_date_epoch = int(start_date.timestamp())
        end_date_epoch = int(end_date.timestamp())
        url = f'https://api.coingecko.com/api/v3/coins/{token_from}/market_chart/range?vs_currency={token_to}&from={start_date_epoch}&to={end_date_epoch}'
        print(f"Historical data URL: {url}")

        response = fetch_data(url)
        historical_data = response['prices']

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

            for data_point in historical_data:
                price_timestamp = data_point[0] / 1000
                blocks_diff = (end_date_epoch - price_timestamp) / BLOCK_TIME_SECONDS
                block_height = int(latest_block_height - blocks_diff)

                if block_height < 1:
                    continue

                price = data_point[1]
                cursor.execute("INSERT OR REPLACE INTO prices (block_height, token, price) VALUES (?, ?, ?)", (block_height, token_name.lower(), price))
                print(f"Inserted data point - block {block_height} : {price}")

            conn.commit()

        print(f'Data initialized successfully for {token_name} token')
    except Exception as e:
        print(f'Failed to initialize data for {token_name} token: {str(e)}')
        raise e

def get_latest_network_block():
    try:
        url = f"{ALLORA_VALIDATOR_API_URL}{URL_QUERY_LATEST_BLOCK}"
        print(f"Latest network block URL: {url}")
        response = requests.get(url)
        response.raise_for_status()

       # Handle case where the response might be a list or dictionary
        if isinstance(response, list):
            block_data = response.json()[0]  # Assume it's a list, get the first element
        else:
            block_data = response.json()  # Assume it's already a dictionary

        # Safely accessing block height
        try:
            latest_block_height = int(block_data['block']['header']['height'])
        except KeyError:
            print("Error: Missing expected keys in block data.")
            latest_block_height = 0  # Handle the error appropriately

        return {'block': {'header': {'height': latest_block_height}}}
    except Exception as e:
        print(f'Failed to get block height: {str(e)}')
        return {}

if __name__ == '__main__':
    tokens = os.environ.get('TOKENS', '').split(',')
    for token in tokens:
        token_parts = token.split(':')
        if len(token_parts) == 2:
            token_name = f"{token_parts[0]}USD"
            token_cg_id = token_parts[1]
            init_price_token(token_name, token_cg_id, 'usd')
    app.run(host='0.0.0.0', port=API_PORT)
