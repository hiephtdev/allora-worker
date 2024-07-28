import os
import requests
from concurrent.futures import ThreadPoolExecutor


# Function to download the URL, called asynchronously by several child processes
def download_url(url, download_path):
    target_file_path = os.path.join(download_path, os.path.basename(url)) 
    if os.path.exists(target_file_path):
        print(f"File already exists: {url}")
        return
    
    response = requests.get(url)
    if response.status_code == 404:
        print(f"File not exist: {url}")
    else:

        # create the entire path if it doesn't exist
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

        with open(target_file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {url} to {target_file_path}")

def get_symbols_id(symbols):
    url = "https://www.mexc.com/api/platform/spot/market-v2/web/symbols"
    response = requests.get(url)
    results = []
    
    if response.status_code == 200:
        response_data = response.json()
        if 'data' in response_data and 'USDT' in response_data['data']:
            for symbol in symbols:
                found = False
                for item in response_data['data']['USDT']:
                    if 'vn' in item and item['vn'] == symbol.upper():
                        results.append({'symbol': symbol, 'id': item.get('id')})
                        found = True
                        break
                if not found:
                    results.append({'symbol': symbol, 'id': None})
    else:
        raise Exception(f"API request failed with status code {response.status_code}")
    
    return results


def download_mexc_minute_data(symbols, interval, year, month, download_path):
    mexc_items = get_symbols_id(symbols)
    if mexc_items is None:
        print("No symbols found")
        return
    base_url = f"https://d2s4an60yebwep.cloudfront.net/SPOT2/kline"
    with ThreadPoolExecutor() as executor:
        for mexc_item in mexc_items:
            if mexc_item['id'] is None:
                continue
            mexcid = mexc_item['id']
            symbol = mexc_item['symbol']
            for day in range(1, 32):  # Assuming days range from 1 to 31
                url = f"{base_url}/{mexcid}/daily/{interval}/{symbol}-{interval}-{year}-{month:02d}-{day:02d}.csv"
                executor.submit(download_url, url, download_path)
              
def download_binance_minute_data(cm_or_um, symbols, interval, year, month, download_path):
    if cm_or_um not in ["cm", "um"]:
        print("CM_OR_UM can be only cm or um")
        return
    base_url = f"https://data.binance.vision/data/futures/{cm_or_um}/daily/klines"
    with ThreadPoolExecutor() as executor:
        for symbol in symbols:
            for day in range(1, 32):  # Assuming days range from 1 to 31
                url = f"{base_url}/{symbol}/{interval}/{symbol}-{interval}-{year}-{month:02d}-{day:02d}.zip"
                executor.submit(download_url, url, download_path)