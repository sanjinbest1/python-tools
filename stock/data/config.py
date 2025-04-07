# Stochastic RSI 配置
STOCHASTIC_RSI = {
    'K_PERIOD': 21,  # %K 周期
    'D_PERIOD': 5,   # %D 周期
    'SMOOTH_K': 5    # %K 平滑周期
}

ADX_CONFIG = {
    "PERIOD": 14,                     # ADX 计算周期
    "WEAK_TREND_THRESHOLD": 25,       # 弱趋势（盘整市场）阈值
    "MEDIUM_TREND_THRESHOLD": 40,     # 中等趋势阈值
    "STRONG_TREND_THRESHOLD": 50,     # 强趋势阈值
}

ATR_CONFIG = {
    "PERIOD": 21,          # ATR 计算周期
    "RECENT_WINDOW": 14,   # 计算最近均值ATR的窗口期
}

# MACD 配置
MACD_CONFIG = {
    'fast_period': 10,  # 快速EMA的周期
    'slow_period': 20,  # 慢速EMA的周期
    'signal_period': 9  # 信号线的周期
}

RSI_CONFIG = {
    "default_window": 14,        # 默认 RSI 计算窗口期
    "window_list": [6, 14, 21],  # 需要计算的多个 RSI 窗口期
    "overbought": 80,            # 超买阈值 - 提高超买门槛
    "oversold": 20,              # 超卖阈值 - 降低超卖门槛
}

BOLLINGER_CONFIG = {
    "WINDOW": 20,  # 计算移动平均线和标准差的窗口大小
    "NUM_STD": 2.5,  # 调整标准差倍数为2.5
}

KELTNER_CONFIG = {
    "PERIOD": 20,         # 计算周期
    "MULTIPLIER": 2.5,    # 增加Multiplier值到2.5
}

OBV_CONFIG = {
    "obv_initial_value": 1000,
    "obv_threshold_positive": 0.3,  # 调整为0.3
    "obv_threshold_negative": -0.3  # 调整为-0.3
}

VWAP_CONFIG = {
    "buy_threshold": 1.5,   # 当股价高于 VWAP 1.5% 以上时，建议买入
    "sell_threshold": -1.5, # 当股价低于 VWAP 1.5% 以上时，建议卖出
}
