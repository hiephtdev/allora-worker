import requests
import sys
import json
import os

INFERENCE_ADDRESS = os.environ["INFERENCE_API_ADDRESS"]
API_KEY = 'UP-9c8c9439cc87403a8ff447f5'  # Replace with your actual API key

def get_token_details(block_height):
    url = f"https://api.upshot.xyz/v2/allora/tokens-oracle/token/{block_height}"
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_token_symbol(block_height):
    token_details = get_token_details(block_height)
    if token_details is None or 'data' not in token_details:
        return None
    if token_details['status'] is not True:
        return None
    if 'token_symbol' not in token_details['data']:
        return None
    return token_details['data']['token_symbol']

def process(token_name):
    response = requests.get(f"{INFERENCE_ADDRESS}/inference/{token_name}")
    content = response.text
    return content

if __name__ == "__main__":
    try:
        if len(sys.argv) < 4:
            value = json.dumps({"error": f"Not enough arguments provided: {len(sys.argv)}, expected 4 arguments: topic_id, blockHeight, blockHeightEval, default_arg"})
        else:
            topic_id = sys.argv[1]
            blockHeight = sys.argv[2]
            blockHeightEval = sys.argv[3]
            default_arg = sys.argv[4]

            token_name = get_token_symbol(blockHeight)
            if token_name is None or token_name == "":
                response_inference = "0.00000001"
                response_dict = {"infererValue": response_inference}
                value = json.dumps(response_dict)
            else:
                response_inference = process(token_name=token_name)
                response_dict = {"infererValue": response_inference}
                value = json.dumps(response_dict)
    except Exception as e:
        value = json.dumps({"error": str(e)})
    print(value)
