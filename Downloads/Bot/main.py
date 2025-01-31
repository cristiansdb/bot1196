import numpy as np
import pandas as pd
import tensorflow as tf
from binance.client import Client
from helpers.data_processor import DataProcessor
from helpers.risk_manager import RiskManager
from config import API_KEY, API_SECRET, SYMBOLS, TIMEFRAME, RISK_PARAMS

class AdvancedTradingBot:
    def __init__(self, testnet=True):
        self.client = Client(API_KEY, API_SECRET, testnet=testnet)
        self.models = self.load_models()
        self.balance = self.get_usdt_balance()
        self.initial_balance = self.balance

    def load_models(self):
        """Carga modelos LSTM preentrenados"""
        return {symbol: tf.keras.models.load_model(f'lstm_models/{symbol}_model.h5') 
                for symbol in SYMBOLS if symbol in ["BTCUSDT", "ETHUSDT", "DOTUSDT"]}

    def get_usdt_balance(self):
        return float(self.client.get_asset_balance(asset='USDT')['free'])

    def get_historical_data(self, symbol):
        klines = self.client.get_klines(
            symbol=symbol,
            interval=TIMEFRAME,
            limit=500
        )
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        return DataProcessor.calculate_technical_indicators(df)

    def predict_with_lstm(self, symbol, data):
        """Predicción combinada LSTM + EMA Cross"""
        processed_data, _, _ = DataProcessor.prepare_lstm_data(data['close'])
        prediction = self.models[symbol].predict(processed_data[-1].reshape(1, 60, 1))[0][0]
        
        # Confirmación con EMA
        ema_cross = data['EMA_50'].iloc[-1] > data['EMA_200'].iloc[-1]
        return 'BUY' if (prediction > data['close'].iloc[-1] and ema_cross) else 'SELL'

    def execute_multi_tp_order(self, symbol, side, quantity):
        """Orden OCO con 3 niveles de Take-Profit"""
        try:
            entry_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
            atr = data['ATR'].iloc[-1] if 'ATR' in data else 0.02 * entry_price
            stop_loss = RiskManager.calculate_stop_loss(entry_price, atr, symbol)
            
            # Crear orden OCO principal
            main_order = self.client.create_oco_order(
                symbol=symbol,
                side=side,
                quantity=quantity * 0.5,  # 50% en TP1
                price=entry_price * (1 + RISK_PARAMS["take_profit_tiers"][0]),
                stopPrice=stop_loss,
                stopLimitPrice=stop_loss * 0.98
            )
            
            # Órdenes adicionales para TP2 y TP3
            for tp in RISK_PARAMS["take_profit_tiers"][1:]:
                self.client.create_order(
                    symbol=symbol,
                    side=Client.SIDE_SELL if side == Client.SIDE_BUY else Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_LIMIT,
                    quantity=quantity * 0.25,  # 25% en TP2 y TP3
                    price=entry_price * (1 + tp),
                    timeInForce=Client.TIME_IN_FORCE_GTC
                )
            
            return main_order
        except Exception as e:
            print(f"Error ejecutando orden: {str(e)}")
            return None

    def run_strategy(self):
        """Ejecuta estrategia para todos los símbolos"""
        for symbol in SYMBOLS:
            try:
                # Paso 1: Obtener y procesar datos
                data = self.get_historical_data(symbol)
                
                # Paso 2: Generar señal
                if symbol in self.models:
                    signal = self.predict_with_lstm(symbol, data)
                else:
                    signal = 'BUY' if data['ADX'].iloc[-1] > 25 else 'HOLD'
                
                # Paso 3: Calcular posición
                atr = data['high'].iloc[-1] - data['low'].iloc[-1]  # ATR simplificado
                position_size = RiskManager.dynamic_position_size(symbol, self.balance, atr)
                
                # Paso 4: Ejecutar orden
                if signal != 'HOLD' and position_size > 0:
                    self.execute_multi_tp_order(symbol, signal, position_size)
                    
                # Actualizar balance y verificar riesgo
                self.balance = self.get_usdt_balance()
                if self.balance < self.initial_balance * (1 + RISK_PARAMS["max_daily_loss"]):
                    print("¡Límite de pérdidas alcanzado! Deteniendo operaciones.")
                    break
                    
            except Exception as e:
                print(f"Error procesando {symbol}: {str(e)}")

    def monitor_performance(self):
        """Monitorea resultados en tiempo real"""
        print(f"\nBalance actual: {self.balance:.2f} USDT")
        print(f"Rendimiento diario: {(self.balance/self.initial_balance-1)*100:.2f}%")

if __name__ == "__main__":
    # Modo prueba (True) o producción (False)
    bot = AdvancedTradingBot(testnet=True)
    
    # Ciclo de trading cada 1 hora
    import schedule
    import time
    
    schedule.every(1).hours.do(bot.run_strategy)
    schedule.every(1).hours.do(bot.monitor_performance)
    
    while True:
        schedule.run_pending()
        time.sleep(1)