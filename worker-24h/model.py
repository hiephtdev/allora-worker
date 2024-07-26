import os
import pickle
from zipfile import ZipFile
import pandas as pd
import numpy as np
import torch
from datetime import datetime
from chronos import ChronosPipeline
from sklearn.model_selection import train_test_split
from updater import download_binance_monthly_data, download_binance_daily_data
from config import data_base_path
import random

forecast_price = {}

binance_data_path = os.path.join(data_base_path, "binance/futures-klines")

def download_data(token):
    cm_or_um = "um"
    symbols = [f"{token.upper()}USDT"]
    intervals = ["1d"]
    years = ["2020", "2021", "2022", "2023", "2024"]
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    download_path = os.path.join(binance_data_path, token.lower())
    download_binance_monthly_data(
        cm_or_um, symbols, intervals, years, months, download_path
    )
    print(f"Downloaded monthly data for {token} to {download_path}.")
    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_month = current_datetime.month
    download_binance_daily_data(
        cm_or_um, symbols, intervals, current_year, current_month, download_path
    )
    print(f"Downloaded daily data for {token} to {download_path}.")

def format_data(token):
    path = os.path.join(binance_data_path, token.lower())
    files = sorted([x for x in os.listdir(path)])

    if len(files) == 0:
        return

    price_df = pd.DataFrame()
    for file in files:
        zip_file_path = os.path.join(path, file)

        if not zip_file_path.endswith(".zip"):
            continue
        
        try:
            with ZipFile(zip_file_path) as myzip:
                with myzip.open(myzip.filelist[0]) as f:
                    header = 0 if f.readline().decode("utf-8").startswith("open_time") else None
                df = pd.read_csv(myzip.open(myzip.filelist[0]), header=header).iloc[:, :11]
                df.columns = [
                    "start_time", "open", "high", "low", "close", "volume",
                    "end_time", "volume_usd", "n_trades", "taker_volume", "taker_volume_usd"
                ]
                df.index = [pd.Timestamp(x + 1, unit="ms") for x in df["end_time"]]
                df.index.name = "date"
                price_df = pd.concat([price_df, df])
        except:
            print(f"Error reading {zip_file_path}")
            continue

    price_df.sort_index().to_csv(os.path.join(data_base_path, f"{token.lower()}_price_data.csv"))

def train_model(token):
    price_data = pd.read_csv(os.path.join(data_base_path, f"{token.lower()}_price_data.csv"))
    df = pd.DataFrame()

    # df["date"] = pd.to_datetime(price_data["date"])
    df["price"] = price_data[["close"]].astype(float)

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
    tokens = ["ETH", "BTC", "SOL"]
    for token in tokens:
        download_data(token)
        format_data(token)
        train_model(token)

if __name__ == "__main__":
    update_data()