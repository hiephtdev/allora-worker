import os
import pickle
from zipfile import ZipFile
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import torch
from chronos import ChronosPipeline
from updater import download_binance_minute_data
from config import data_base_path
import random

forecast_price = {}

binance_data_path = os.path.join(data_base_path, "binance/futures-klines")

def download_data(token):
    cm_or_um = "um"
    symbols = [f"{token.upper()}USDT"]
    interval = "5m"  # 5 phút
    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_month = current_datetime.month
    download_path = os.path.join(binance_data_path, token.lower())
    
    # Download dữ liệu 5 phút
    download_binance_minute_data(
        cm_or_um, symbols, interval, current_year, current_month, download_path
    )
    print(f"Downloaded minute data for {token} to {download_path}.")

def format_data(token):
    path = os.path.join(binance_data_path, token.lower())
    files = sorted([x for x in os.listdir(path)])

    # Không có file nào để xử lý
    if len(files) == 0:
        print(f"No data files found for {token}")
        return

    price_df = pd.DataFrame()
    for file in files:
        zip_file_path = os.path.join(path, file)

        if not zip_file_path.endswith(".zip"):
            continue
        
        try:
            myzip = ZipFile(zip_file_path)
        except:
            print(f"Error reading {zip_file_path}")
            continue
        
        with myzip.open(myzip.filelist[0]) as f:
            line = f.readline()
            header = 0 if line.decode("utf-8").startswith("open_time") else None
        df = pd.read_csv(myzip.open(myzip.filelist[0]), header=header).iloc[:, :11]
        df.columns = [
            "start_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "end_time",
            "volume_usd",
            "n_trades",
            "taker_volume",
            "taker_volume_usd",
        ]
        df.index = [pd.Timestamp(x + 1, unit="ms") for x in df["end_time"]]
        df.index.name = "date"
        price_df = pd.concat([price_df, df])

    if price_df.empty:
        print(f"No valid data found for {token}")
        return

    price_df.sort_index().to_csv(os.path.join(data_base_path, f"{token.lower()}_price_data.csv"))

def train_model(token):
    # Load the token price data
    price_data = pd.read_csv(os.path.join(data_base_path, f"{token.lower()}_price_data.csv"))
    df = pd.DataFrame()

    # Convert 'date' to datetime
    price_data["date"] = pd.to_datetime(price_data["date"])

    # Calculate the mean price
    # price_data["price"] = price_data[["open", "close", "high", "low"]].mean(axis=1)
    # price_data["price"] = price_data[["close"]].astype(float)

    # Set the date column as the index for resampling
    price_data.set_index("date", inplace=True)

    # Resample the data to 10-minute frequency and compute the mean price
    df = price_data.resample('10T').mean()

    # Reset the index to have 'date' as a column again
    df.reset_index(inplace=True)
    df["date"] = df["date"].map(pd.Timestamp.timestamp)

    # df["date"] = pd.to_datetime(price_data["date"])
    df["price"] = df[["close"]].astype(float)

    # print(df.head())

    context = torch.tensor(df["price"].values)
    prediction_length = 1 # Dự đoán giá tiếp theo

    # Huấn luyện mô hình Chronos-T5-Tiny 
    pipeline = ChronosPipeline.from_pretrained("amazon/chronos-t5-tiny", device_map="auto", torch_dtype=torch.bfloat16)
    forecast = pipeline.predict(context, prediction_length, num_samples=20)

    forecast = np.unique(forecast)
    print(f"List forecast for {token}: {forecast}")

    # Lấy giá thấp nhất và cao nhất
    min_price = np.min(forecast)
    max_price = np.max(forecast)

    # Chọn ngẫu nhiên một giá trị giữa giá thấp nhất và giá cao nhất, để tránh dự đoán giống nhau
    price_predict = random.uniform(min_price, max_price)
    forecast_price[token] = price_predict

    # median = np.median(forecast.numpy(), axis=1)
    # forecast_price[token] = median[0][-1]

    print(f"Forecasted price for {token}: {forecast_price[token]}")

def update_data():
    tokens = ["ETH", "BNB", "ARB"]
    for token in tokens:
        download_data(token)
        format_data(token)
        train_model(token)

if __name__ == "__main__":
    update_data()