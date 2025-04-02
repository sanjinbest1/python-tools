import pandas as pd
import numpy as np


def calculate_atr(stock_data, period=14):
    """
    计算真实波动幅度均值（ATR）

    参数:
    stock_data (pd.DataFrame): 股票数据，包含最高价、最低价、收盘价
    period (int): 计算 ATR 的周期，默认为 14

    返回:
    pd.Series: ATR 值
    """
    high = stock_data['high']
    low = stock_data['low']
    close = stock_data['close']

    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = np.abs(high - prev_close)
    tr3 = np.abs(low - prev_close)
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.rolling(window=period).mean()
    return atr

def generate_atr_operation_suggestion(atr_data):
    """
    根据 ATR 指标生成操作建议

    参数:
    atr_data (pd.Series): ATR 值

    返回:
    str: 操作建议
    """
    latest_atr = atr_data.iloc[-1]
    recent_mean_atr = atr_data.rolling(window=10).mean().iloc[-1]

    if latest_atr > recent_mean_atr:
        detailed_suggestion = "ATR - {:.2f}, 均值 - {:.2f}, 市场波动性增加，操作需谨慎，可适当调整止损止盈。".format(latest_atr, recent_mean_atr)
        simple_suggestion = "观望"
    elif latest_atr < recent_mean_atr:
        detailed_suggestion = "ATR - {:.2f}, 均值 - {:.2f}, 市场波动性降低，可考虑更积极的操作策略。".format(latest_atr, recent_mean_atr)
        simple_suggestion = "买入"
    else:
        detailed_suggestion = "ATR - {:.2f}, 均值 - {:.2f}, 指标无明显变化，维持当前操作策略。".format(latest_atr, recent_mean_atr)
        simple_suggestion = "观望"

    print(detailed_suggestion)
    return simple_suggestion
