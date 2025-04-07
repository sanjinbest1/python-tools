import pandas as pd
import numpy as np
from stock.data.config import ADX_CONFIG  # 从配置文件导入参数

def calculate_dm(high, low):
    """计算正向/负向趋向变动（+DM / -DM）"""
    up_move = high.diff()
    down_move = low.diff()

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move < 0), -down_move, 0.0)

    return pd.Series(plus_dm, index=high.index), pd.Series(minus_dm, index=high.index)

def wilder_smoothing(series, period):
    """Wilder's 平滑法，用于 TR / DM 平滑"""
    result = series.copy()
    result.iloc[:period] = series.iloc[:period].sum()
    for i in range(period, len(series)):
        result.iloc[i] = result.iloc[i - 1] - (result.iloc[i - 1] / period) + series.iloc[i]
    return result

def calculate_adx_safe(stock_data, epsilon=1e-10):
    """
    安全计算 ADX 指标，采用 Wilder's 平滑，提升准确性

    参数:
    stock_data (pd.DataFrame): 包含 'high', 'low', 'close'
    返回:
    pd.Series: ADX 序列
    """

    period = ADX_CONFIG["PERIOD"]

    high = pd.to_numeric(stock_data['high'], errors='coerce')
    low = pd.to_numeric(stock_data['low'], errors='coerce')
    close = pd.to_numeric(stock_data['close'], errors='coerce')
    prev_close = close.shift(1)

    # True Range (TR)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    plus_dm, minus_dm = calculate_dm(high, low)

    # Wilder's smoothing
    tr_smooth = wilder_smoothing(true_range, period)
    plus_dm_smooth = wilder_smoothing(plus_dm, period)
    minus_dm_smooth = wilder_smoothing(minus_dm, period)

    # +DI / -DI
    plus_di = 100 * (plus_dm_smooth / (tr_smooth + epsilon))
    minus_di = 100 * (minus_dm_smooth / (tr_smooth + epsilon))

    # DX & ADX
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di + epsilon))
    adx = wilder_smoothing(dx, period)

    return adx.fillna(0)

def generate_adx_operation_suggestion(adx_data):
    """
    根据 ADX 指标生成操作建议
    """
    latest_adx = adx_data.iloc[-1]
    suggestion_text = f"ADX - 当前 ADX 指数为 {latest_adx:.2f}，"

    if latest_adx < ADX_CONFIG['WEAK_TREND_THRESHOLD']:
        suggestion_text += (
            "\n\n市场缺乏明显趋势，可能处于横盘或震荡整理阶段。\n"
            "📌 建议：\n"
            "  - 趋势较弱，避免盲目操作，宜【观望】。\n"
            "  - 等待进一步信号确认。"
        )
        suggestion_level = "观望"
    elif ADX_CONFIG['WEAK_TREND_THRESHOLD'] <= latest_adx < ADX_CONFIG['MEDIUM_TREND_THRESHOLD']:
        suggestion_text += (
            "\n\n趋势初步形成，但仍较弱。\n"
            "📌 建议：\n"
            "  - 保持【观望】或轻仓试探，确认趋势方向再操作。"
        )
        suggestion_level = "观望"
    elif ADX_CONFIG['MEDIUM_TREND_THRESHOLD'] <= latest_adx < ADX_CONFIG['STRONG_TREND_THRESHOLD']:
        suggestion_text += (
            "\n\n市场呈现明显趋势，方向明确。\n"
            "📌 建议：\n"
            "  - 顺势操作，适时【买入】或加仓。\n"
            "  - 同时注意短期调整风险。"
        )
        suggestion_level = "买入"
    else:
        suggestion_text += (
            "\n\n市场处于强烈单边趋势中，动能旺盛。\n"
            "📌 建议：\n"
            "  - 积极顺势操作，可【买入】或【持有】。\n"
            "  - 建议设置止盈止损，防范突发回调风险。"
        )
        suggestion_level = "买入"

    print(suggestion_text)
    print("-----------------------------------------------------------------------------------------------------")
    return suggestion_level
