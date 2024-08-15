import os
from app_utils import init_price_token
import sys

# Initialize tokens at the start
def initialize_tokens():
    try:
        tokens = os.environ.get('TOKENS', '').split(',')
        print(f"Tokens: {tokens}")
        if tokens and len(tokens) > 0:
            for token in tokens:
                token_parts = token.split(':')
                print(f"Token parts: {token_parts}")
                if len(token_parts) == 2:
                    token_name = f"{token_parts[0]}USD"
                    print(f"Initializing data for {token_name} token")
                    init_price_token(token_parts[0], token_name, 'usd')
    except Exception as e:
        print(f"Failed to initialize tokens: {str(e)}")
    finally:
        print("Tokens initialized successfully")
        sys.exit(0)

# Ensure tokens are initialized whether the script is run directly or through Gunicorn
initialize_tokens()