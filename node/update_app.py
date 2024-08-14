import os
import sys
import requests

def update_token_price(api_address, token_symbol, token_from):
    try:
        token_name = f"{token_symbol}USD"
        url = f"{api_address}/update/{token_name}/{token_from}/usd"
        response = requests.get(url)
        
        if response.status_code == 200:
            print(f"Successfully updated {token_name}: {response.text}")
        else:
            print(f"Failed to update {token_name}. Status code: {response.status_code}")
            print("Error:", response.text)
    except Exception as e:
        print(f"Failed to update data for {token_symbol} token: {str(e)}")

def main():
    try:
        data_provider_api_address = os.environ['DATA_PROVIDER_API_ADDRESS']
        tokens = os.environ.get('TOKENS', '').split(',')

        for token in tokens:
            if ':' in token:
                token_symbol, token_from = token.split(':')
                update_token_price(data_provider_api_address, token_symbol, token_from)
            else:
                print(f"Invalid token format: {token}")
    except KeyError as e:
        print(f"Environment variable {str(e)} not found.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()
