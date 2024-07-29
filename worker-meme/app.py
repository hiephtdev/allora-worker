from flask import Flask, Response
import requests
import json
import pandas as pd
import torch
from chronos import ChronosPipeline

# create our Flask app
app = Flask(__name__)
 
# define the Hugging Face model we will use
model_name = "amazon/chronos-t5-tiny"
 
coingecko_api_key = ""
 
# define our endpoint
@app.route("/inference/<string:token>")
def get_inference(token):
    """Generate inference for given token."""
    if not token:
        error_msg = "Token is required" if not token else "Token not supported"
        return Response(json.dumps({"error": error_msg}), status=400, mimetype='application/json')
    try:
        # use a pipeline as a high-level helper
        pipeline = ChronosPipeline.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )
    except Exception as e:
        return Response(json.dumps({"pipeline error": str(e)}), status=500, mimetype='application/json')
 
    # get the data from Coingecko
    # here we'll use last 30 days of BTC/USD
    url = f"https://api.coingecko.com/api/v3/coins/{token}/market_chart?vs_currency=usd&days=1&interval=daily"
 
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": coingecko_api_key # replace with your API key
    }
 
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["prices"])
        df.columns = ["date", "price"]
        df["date"] = pd.to_datetime(df["date"], unit = "ms")
        df = df[:-1] # removing today's price
        print(df.tail(5))
    else:
        return Response(json.dumps({"Failed to retrieve data from the API": str(response.text)}), 
                        status=response.status_code, 
                        mimetype='application/json')
 
    # define the context and the prediction length
    context = torch.tensor(df["price"])
    prediction_length = 1
 
    try:
        forecast = pipeline.predict(context, prediction_length)  # shape [num_series, num_samples, prediction_length]
        print(forecast[0].mean().item()) # taking the mean of the forecasted prediction
        return Response(str(forecast[0].mean().item()), status=200)
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')
 
# run our Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8013, debug=True)