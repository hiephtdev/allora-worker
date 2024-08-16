import os
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from zipfile import ZipFile
import pandas as pd
import sqlite3
from app_config import DATABASE_PATH, BLOCK_TIME_SECONDS, DATA_BASE_PATH, ALLORA_VALIDATOR_API_URL, URL_QUERY_LATEST_BLOCK

# Function to check and create the table if not exists
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

def download_binance_data(symbol, interval, year, month, download_path):
    base_url = f"https://data.binance.vision/data/futures/um/daily/klines"
    with ThreadPoolExecutor() as executor:
        for day in range(1, 32):  # Assuming days range from 1 to 31
            url = f"{base_url}/{symbol}/{interval}/{symbol}-{interval}-{year}-{month:02d}-{day:02d}.zip"
            executor.submit(download_url, url, download_path)

def download_url(url, download_path):
    target_file_path = os.path.join(download_path, os.path.basename(url)) 
    if os.path.exists(target_file_path):
        print(f"File already exists: {url}")
        return
    
    response = requests.get(url)
    if response.status_code == 404:
        print(f"File does not exist: {url}")
    else:
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        with open(target_file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {url} to {target_file_path}")

def extract_and_process_binance_data(token_name, download_path, start_date_epoch, end_date_epoch, latest_block_height):
    files = sorted([x for x in os.listdir(download_path) if x.endswith('.zip')])

    if len(files) == 0:
        print(f"No data files found for {token_name}")
        return

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        for file in files:
            zip_file_path = os.path.join(download_path, file)

            try:
                with ZipFile(zip_file_path) as myzip:
                    with myzip.open(myzip.filelist[0]) as f:
                        df = pd.read_csv(f, header=None)
                        df.columns = [
                            "open_time", "open", "high", "low", "close",
                            "volume", "close_time", "quote_volume", 
                            "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"
                        ]
                        
                        df['close_time'] = pd.to_numeric(df['close_time'], errors='coerce')
                        df.dropna(subset=['close_time'], inplace=True)
                        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

                        for _, row in df.iterrows():
                            price_timestamp = row['close_time'].timestamp()
                            if price_timestamp < start_date_epoch or price_timestamp > end_date_epoch:
                                continue

                            blocks_diff = (end_date_epoch - price_timestamp) / BLOCK_TIME_SECONDS
                            block_height = int(latest_block_height - blocks_diff)

                            if block_height < 1:
                                continue

                            price = row['close']
                            cursor.execute("INSERT OR REPLACE INTO prices (block_height, token, price) VALUES (?, ?, ?)", 
                                           (block_height, token_name.lower(), price))
                            print(f"{token_name} - {price_timestamp} - Inserted data point - block {block_height} : {price}")

            except Exception as e:
                print(f"Error reading {zip_file_path}: {str(e)}")
                continue

        conn.commit()

# Function to get the latest network block
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

        try:
            latest_block_height = int(block_data['block']['header']['height'])
            print(f"Latest block height: {latest_block_height}")
        except KeyError:
            print("Error: Missing expected keys in block data.")
            latest_block_height = 0

        return {'block': {'header': {'height': latest_block_height}}}
    except Exception as e:
        print(f'Failed to get block height: {str(e)}')
        return {}

# Initialize price token function
def init_price_token(symbol, token_name, token_to):
    try:
        check_create_table()

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM prices WHERE token=?", (token_name.lower(),))
            count = cursor.fetchone()[0]

        if count > 10000:
            print(f'Data already exists for {token_name} token, {count} entries')
            return
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=31)

        block_data = get_latest_network_block()
        latest_block_height = int(block_data['block']['header']['height'])

        start_date_epoch = int(start_date.timestamp())
        end_date_epoch = int(end_date.timestamp())

        symbol = f"{symbol.upper()}{token_to.upper()}T"
        interval = "1m"  # 1-minute interval data
        binance_data_path = os.path.join(DATA_BASE_PATH, "binance/futures-klines")
        download_path = os.path.join(binance_data_path, symbol.lower())
        download_binance_data(symbol, interval, end_date.year, end_date.month, download_path)
        extract_and_process_binance_data(token_name, download_path, start_date_epoch, end_date_epoch, latest_block_height)

        print(f'Data initialized successfully for {token_name} token')
    except Exception as e:
        print(f'Failed to initialize data for {token_name} token: {str(e)}')
        raise e