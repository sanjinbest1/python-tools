import pandas as pd
import numpy as np


def calculate_dm(high, low, period=14):
    """
    计算方向运动指标（DM）

    参数:
    high (pd.Series): 最高价序列
    low (pd.Series): 最低价序列
    period (int): 计算周期，默认为 14

    返回:
    +DM (pd.Series): 正方向运动指标
    -DM (pd.Series): 负方向运动指标
    """
    prev_high = high.shift(1)
    prev_low = low.shift(1)

    plus_dm = ((high > prev_high) & (low > prev_low)).astype(int) * (high - prev_high)
    minus_dm = ((low < prev_low) & (high < prev_high)).astype(int) * (prev_low - low)

    plus_dm_smoothed = plus_dm.rolling(window=period).sum()
    minus_dm_smoothed = minus_dm.rolling(window=period).sum()

    return plus_dm_smoothed, minus_dm_smoothed


def calculate_adx(stock_data, period=14):
    """
    计算平均趋向指数（ADX）

    参数:
    stock_data (pd.DataFrame): 股票数据，包含最高价、最低价、收盘价
    period (int): 计算周期，默认为 14

    返回:
    pd.Series: ADX 值
    """
    # 将 high, low, close 列转换为数值类型
    stock_data['high'] = pd.to_numeric(stock_data['high'], errors='coerce')
    stock_data['low'] = pd.to_numeric(stock_data['low'], errors='coerce')
    stock_data['close'] = pd.to_numeric(stock_data['close'], errors='coerce')

    high = stock_data['high']
    low = stock_data['low']
    close = stock_data['close']

    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = np.abs(high - prev_close)
    tr3 = np.abs(low - prev_close)
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    truerange_smoothed = true_range.rolling(window=period).mean()

    plus_dm, minus_dm = calculate_dm(high, low, period)

    dx_numerator = np.abs((plus_dm / truerange_smoothed) - (minus_dm / truerange_smoothed))
    dx_denominator = (plus_dm / truerange_smoothed) + (minus_dm / truerange_smoothed)
    dx = (dx_numerator / dx_denominator) * 100

    adx = dx.rolling(window=period).mean()
    return adx

def generate_adx_operation_suggestion(adx_data):
    """
    根据 ADX 指标生成操作建议

    参数:
    adx_data (pd.Series): ADX 值

    返回:
    str: 操作建议
    """
    latest_adx = adx_data.iloc[-1]
    if latest_adx < 20:
        print("ADX 小于 20，显示趋势较弱，市场可能处于盘整状态，建议观望。")
        return "观望"
    elif 20 <= latest_adx < 40:
        print("ADX 在 20 到 40 之间，显示趋势开始形成，可关注趋势发展。")
        return "观望"
    elif 40 <= latest_adx < 60:
        print("ADX 在 40 到 60 之间，显示趋势较强，可考虑跟随趋势操作。")
        return "买入"
    elif latest_adx >= 60:
        print("ADX 大于等于 60，显示趋势非常强，可坚定跟随趋势，但需注意趋势反转风险。")
        return "买入"
    else:
        print("ADX 指标无明显指示，建议观望。")
        return "观望"

