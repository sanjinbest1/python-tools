import pandas as pd
import numpy as np
from stock.data.config import ADX_CONFIG  # 从配置文件导入参数


def calculate_dm(high, low):
    """
    计算方向运动指标（DM）

    参数:
    high (pd.Series): 最高价序列
    low (pd.Series): 最低价序列

    返回:
    +DM (pd.Series): 正方向运动指标
    -DM (pd.Series): 负方向运动指标
    """
    period = ADX_CONFIG['PERIOD']

    prev_high = high.shift(1)
    prev_low = low.shift(1)

    plus_dm = np.where((high > prev_high) & (low > prev_low), high - prev_high, 0)
    minus_dm = np.where((low < prev_low) & (high < prev_high), prev_low - low, 0)

    plus_dm_smoothed = pd.Series(plus_dm).rolling(window=period).sum()
    minus_dm_smoothed = pd.Series(minus_dm).rolling(window=period).sum()

    return plus_dm_smoothed, minus_dm_smoothed


def calculate_adx(stock_data):
    """
    计算平均趋向指数（ADX）

    参数:
    stock_data (pd.DataFrame): 股票数据，包含最高价、最低价、收盘价

    返回:
    pd.Series: ADX 值
    """
    period = ADX_CONFIG['PERIOD']

    high = pd.to_numeric(stock_data['high'], errors='coerce')
    low = pd.to_numeric(stock_data['low'], errors='coerce')
    close = pd.to_numeric(stock_data['close'], errors='coerce')

    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = np.abs(high - prev_close)
    tr3 = np.abs(low - prev_close)
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    truerange_smoothed = true_range.rolling(window=period).mean()

    plus_dm, minus_dm = calculate_dm(high, low)

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
    simple_suggestion = "观望"

    if latest_adx < ADX_CONFIG['WEAK_TREND_THRESHOLD']:
        detailed_suggestion = "ADX - {:.2f}, 趋势较弱，市场可能处于盘整状态，建议观望。".format(latest_adx)
    elif ADX_CONFIG['WEAK_TREND_THRESHOLD'] <= latest_adx < ADX_CONFIG['MEDIUM_TREND_THRESHOLD']:
        detailed_suggestion = "ADX - {:.2f}, 趋势开始形成，可关注趋势发展。".format(latest_adx)
    elif ADX_CONFIG['MEDIUM_TREND_THRESHOLD'] <= latest_adx < ADX_CONFIG['STRONG_TREND_THRESHOLD']:
        detailed_suggestion = "ADX - {:.2f}, 趋势较强，可考虑跟随趋势操作。".format(latest_adx)
        simple_suggestion = "买入"
    else:
        detailed_suggestion = "ADX - {:.2f}, 趋势非常强，可坚定跟随趋势，但需注意趋势反转风险。".format(latest_adx)
        simple_suggestion = "买入"

    print(detailed_suggestion)
    return simple_suggestion
