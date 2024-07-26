import requests
import sys
import json

API_KEY = 'UP-'  # Replace with your actual API key

def get_token_details(block_height):
    url = f"https://api.upshot.xyz/v2/allora/tokens-oracle/token/{block_height}"
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.json()

def process(block_height):
    token_details = get_token_details(block_height)
    # Assuming token_details contains a 'price' field or similar for prediction
    return token_details.get('price', 'No price found')

if __name__ == "__main__":
    try:
        if len(sys.argv) < 4:
            value = json.dumps({"error": f"Not enough arguments provided: {len(sys.argv)}, expected 4 arguments: topic_id, blockHeight, blockHeightEval, default_arg"})
        else:
            topic_id = sys.argv[1]
            blockHeight = sys.argv[2]
            blockHeightEval = sys.argv[3]
            default_arg = sys.argv[4]

            response_inference = process(block_height=blockHeight)
            response_dict = {"infererValue": response_inference}
            value = json.dumps(response_dict)
    except Exception as e:
        value = json.dumps({"error": str(e)})
    print(value)
