import json
from flask import Flask, Response
from model import download_data, format_data, train_model
from model import forecast_price

app = Flask(__name__)

def update_data():
    """Download price data, format data and train model."""
    tokens = ["ETH", "BTC", "SOL"]
    for token in tokens:
        download_data(token)
        format_data(token)
        train_model(token)

def get_token_inference(token):
    return forecast_price.get(token, 0)

@app.route("/inference/<string:token>")
def generate_inference(token):
    """Generate inference for given token."""
    if not token or token not in ["ETH", "BTC", "SOL"]:
        error_msg = "Token is required" if not token else "Token not supported"
        return Response(json.dumps({"error": error_msg}), status=400, mimetype='application/json')

    try:
        inference = get_token_inference(token)
        return Response(str(inference), status=200)
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')

@app.route("/update")
def update():
    """Update data and return status."""
    try:
        update_data()
        return "0"
    except Exception:
        return "1"

if __name__ == "__main__":
    update_data()
    app.run(host="0.0.0.0", port=8011)