import os
import numpy as np
import sqlite3
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import joblib
from app_config import DATABASE_PATH

# Ensure the models directory exists
os.makedirs('models', exist_ok=True)

# Fetch data from the database
def load_data(token_name):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT price FROM prices 
            WHERE token=?
            ORDER BY block_height ASC
        """, (token_name,))
        result = cursor.fetchall()
    return np.array([x[0] for x in result]).reshape(-1, 1)

# Prepare data for LSTM
def prepare_data_for_lstm(data, look_back, prediction_horizon):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    X, Y = [], []
    for i in range(len(scaled_data) - look_back - prediction_horizon):
        X.append(scaled_data[i:(i + look_back), 0])
        Y.append(scaled_data[i + look_back + prediction_horizon - 1, 0])
    X = np.array(X)
    Y = np.array(Y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, Y, scaler

# Create LSTM model
def create_lstm_model(look_back):
    model = Sequential()
    model.add(LSTM(100, return_sequences=True, input_shape=(look_back, 1)))
    model.add(Dropout(0.2))  # Optional: Prevent overfitting
    model.add(LSTM(100))
    model.add(Dense(50, activation='relu'))  # Optional: Extra Dense layer
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Generalized training function with scaler saved
def train_and_save_model(token_name, look_back, prediction_horizon):
    try:
        print(f"Training model for {token_name} with a {prediction_horizon}-minute horizon.")
        
        data = load_data(token_name)
        X, Y, scaler = prepare_data_for_lstm(data, look_back, prediction_horizon)
        
        model = create_lstm_model(look_back)
        model.fit(X, Y, epochs=10, batch_size=1, verbose=2)
        
        # Save the model using the native Keras format
        model_path = f'models/{token_name.lower()}_model_{prediction_horizon}m.keras'
        model.save(model_path, save_format='keras')
        
        # Save the scaler
        scaler_path = f'models/{token_name.lower()}_scaler_{prediction_horizon}m.pkl'
        joblib.dump(scaler, scaler_path)
        
        print(f"Model and scaler for {token_name} ({prediction_horizon}-minute prediction) saved to {model_path} and {scaler_path}")
    
    except Exception as e:
        print(f"Error occurred while training model for {token_name}: {e}")

# Training for different time horizons
time_horizons = {
    '10m': (10, 10),       # LOOK_BACK=10, PREDICTION_HORIZON=10
    '20m': (10, 20),       # LOOK_BACK=10, PREDICTION_HORIZON=20
    '24h': (1440, 1440)    # LOOK_BACK=1440, PREDICTION_HORIZON=1440
}

for token in ['ETH', 'ARB', 'BTC', 'SOL', 'BNB']:
    for horizon_name, (look_back, prediction_horizon) in time_horizons.items():
        train_and_save_model(f"{token}USD".lower(), look_back, prediction_horizon)
