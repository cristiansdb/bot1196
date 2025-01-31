import os
from dotenv import load_dotenv

load_dotenv()

# Configuración Binance
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Parámetros de Trading
SYMBOLS = ["BTCUSDT", "ETHUSDT", "DOTUSDT", "SOLUSDT", "ADAUSDT", "PEPEUSDT"]
TIMEFRAME = "1h"

# Gestión de Riesgos
RISK_PARAMS = {
    "max_daily_loss": -0.05,  # -5% diario
    "take_profit_tiers": [0.02, 0.05, 0.10],  # 2%, 5%, 10%
    "position_allocations": {
        "BTCUSDT": 0.3,
        "ETHUSDT": 0.25,
        "DOTUSDT": 0.15,
        "SOLUSDT": 0.1,
        "ADAUSDT": 0.1,
        "PEPEUSDT": 0.1
    },
    "volatility_multipliers": {
        "BTCUSDT": 1.2,
        "ETHUSDT": 1.5,
        "DOTUSDT": 2.0,
        "SOLUSDT": 2.5,
        "ADAUSDT": 2.2,
        "PEPEUSDT": 3.0
    }
}