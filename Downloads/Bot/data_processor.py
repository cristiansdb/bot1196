import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class DataProcessor:
    @staticmethod
    def prepare_lstm_data(data, window=60):
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data.values.reshape(-1,1))
        
        X, y = [], []
        for i in range(window, len(scaled_data)):
            X.append(scaled_data[i-window:i])
            y.append(scaled_data[i])
        return np.array(X), np.array(y), scaler

    @staticmethod
    def calculate_technical_indicators(df):
        df['EMA_50'] = EMAIndicator(df['close'], 50).ema_indicator()
        df['EMA_200'] = EMAIndicator(df['close'], 200).ema_indicator()
        df['ADX'] = ADXIndicator(df['high'], df['low'], df['close'], 14).adx()
        return df