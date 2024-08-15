import os
import sys
import sqlite3
from app_config import DATABASE_PATH
from app_utils import fetch_cg_data, get_latest_network_block, check_create_table
from concurrent.futures import ThreadPoolExecutor

def update_price(token_name, token_from, token_to='usd'):
    try:
        check_create_table()
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={token_from}&vs_currencies={token_to}'
        prices = fetch_cg_data(url)

        if token_from.lower() not in prices:
            print(f"Invalid token ID: {token_from}")
            return

        price = prices[token_from.lower()][token_to.lower()]
        block_data = get_latest_network_block()
        latest_block_height = block_data['block']['header']['height']
        token = token_name.lower()

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO prices (block_height, token, price) VALUES (?, ?, ?)", (latest_block_height, token, price))
            conn.commit()

        print(f"Inserted data point {latest_block_height} : {price}")
    except Exception as e:
        print(f"Failed to update {token_name} price: {str(e)}")

def main():
    try:
        tokens = os.environ.get('TOKENS', '').split(',')        
        with ThreadPoolExecutor() as executor:
            executor.map(lambda token: update_price(f"{token.split(':')[0]}USD", token.split(':')[1], 'usd'), tokens)
    except KeyError as e:
        print(f"Environment variable {str(e)} not found.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()
