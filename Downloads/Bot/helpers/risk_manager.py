class RiskManager:
    @staticmethod
    def dynamic_position_size(symbol, balance, volatility):
        allocation = RISK_PARAMS["position_allocations"][symbol]
        multiplier = RISK_PARAMS["volatility_multipliers"][symbol]
        return (balance * allocation) / (volatility * multiplier)

    @staticmethod
    def calculate_stop_loss(entry_price, atr, symbol):
        multiplier = RISK_PARAMS["volatility_multipliers"][symbol]
        return entry_price - (atr * multiplier)