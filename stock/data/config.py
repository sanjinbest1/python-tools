# config.py

# ------------------------------------------------------
# 技术指标配置
# ------------------------------------------------------

# Stochastic RSI 配置
STOCHASTIC_RSI = {
    'K_PERIOD': 21,  # %K 周期
    'D_PERIOD': 5,   # %D 周期
    'SMOOTH_K': 5    # %K 平滑周期
}


ADX_CONFIG = {
    "PERIOD": 14,                     # ADX 计算周期
    "WEAK_TREND_THRESHOLD": 20,       # 弱趋势（盘整市场）阈值
    "MEDIUM_TREND_THRESHOLD": 40,     # 中等趋势阈值
    "STRONG_TREND_THRESHOLD": 60,     # 强趋势阈值
}



ATR_CONFIG = {
    "PERIOD": 14,          # ATR 计算周期
    "RECENT_WINDOW": 10,   # 计算最近均值ATR的窗口期
}


# stock/data/config.py

BOLLINGER_CONFIG = {
    "WINDOW": 20,  # 计算移动平均线和标准差的窗口大小
    "NUM_STD": 2,  # 标准差的倍数
}


# config.py

KELTNER_CONFIG = {
    "PERIOD": 20,         # 计算周期
    "MULTIPLIER": 2,      # ATR 乘数
}


# config.py

MACD_CONFIG = {
    "FAST_PERIOD": 5,       # 快速EMA的时间窗口
    "SLOW_PERIOD": 13,      # 慢速EMA的时间窗口
    "SIGNAL_PERIOD": 5      # 信号线的时间窗口
}

OBV_CONFIG = {
    "obv_initial_value": 1000,
    "obv_threshold_positive": 0.5,
    "obv_threshold_negative": -0.5
}

# stock/data/config.py

# MACD 配置
MACD_CONFIG = {
    'fast_period': 12,  # 快速EMA的周期
    'slow_period': 26,  # 慢速EMA的周期
    'signal_period': 9  # 信号线的周期
}

# config.py

RSI_CONFIG = {
    "default_window": 14,        # 默认 RSI 计算窗口期
    "window_list": [6, 14, 21],  # 需要计算的多个 RSI 窗口期
    "overbought": 70,            # 超买阈值
    "oversold": 30,              # 超卖阈值
}


# config.py

VWAP_CONFIG = {
    "buy_threshold": 1.0,   # 当股价高于 VWAP 1% 以上时，建议买入
    "sell_threshold": -1.0, # 当股价低于 VWAP 1% 以上时，建议卖出
}


