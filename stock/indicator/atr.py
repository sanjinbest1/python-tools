import pandas as pd
import numpy as np
from stock.data.config import ATR_CONFIG  # 从配置文件导入参数

def wilder_smoothing(series, period):
    """Wilder’s Smoothing，用于更准确的 ATR"""
    result = series.copy()
    result.iloc[:period] = series.iloc[:period].mean()
    for i in range(period, len(series)):
        result.iloc[i] = (result.iloc[i - 1] * (period - 1) + series.iloc[i]) / period
    return result

def calculate_atr(stock_data):
    """
    使用 Wilder 方法计算 ATR（Average True Range）

    参数:
    stock_data (pd.DataFrame): 股票数据，包含 'high', 'low', 'close'

    返回:
    pd.Series: ATR 序列
    """
    period = ATR_CONFIG["PERIOD"]

    high = pd.to_numeric(stock_data["high"], errors="coerce")
    low = pd.to_numeric(stock_data["low"], errors="coerce")
    close = pd.to_numeric(stock_data["close"], errors="coerce")

    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = wilder_smoothing(true_range, period)
    return atr.fillna(0)

def generate_atr_operation_suggestion(atr_data):
    """
    根据 ATR 指标生成操作建议，结合短期均值分析波动性变化

    参数:
    atr_data (pd.Series): ATR 指标序列

    返回:
    str: 操作建议文案
    """
    recent_window = ATR_CONFIG["RECENT_WINDOW"]

    latest_atr = atr_data.iloc[-1]
    recent_mean_atr = atr_data.rolling(window=recent_window).mean().iloc[-1]
    atr_ratio = (latest_atr / recent_mean_atr) if recent_mean_atr != 0 else 1

    suggestion_text = f"ATR - 当前 ATR 值为 {latest_atr:.2f}，过去 {recent_window} 日均值为 {recent_mean_atr:.2f}，波动比率为 {atr_ratio:.2f}。"

    if atr_ratio > 1.2:
        suggestion_text += (
            "\n\n📈 市场波动显著增加，可能出现大幅振荡或行情转折。\n"
            "📌 建议：\n"
            "  - 谨慎操作，避免追涨杀跌。\n"
            "  - 可考虑收紧止损保护，降低仓位波动风险。"
        )
        suggestion_level = "观望"
    elif atr_ratio < 0.8:
        suggestion_text += (
            "\n\n📉 市场波动较小，行情较为稳定。\n"
            "📌 建议：\n"
            "  - 适合短线操作或趋势跟踪策略。\n"
            "  - 可适度加仓或关注突破机会。"
        )
        suggestion_level = "买入"
    else:
        suggestion_text += (
            "\n\n⚖ 当前波动性稳定，尚无明显变化趋势。\n"
            "📌 建议：\n"
            "  - 持续观察，维持当前策略。\n"
            "  - 配合其他指标（如ADX/RSI）确认入场时机。"
        )
        suggestion_level = "观望"

    print(suggestion_text)
    print("-----------------------------------------------------------------------------------------------------")
    return suggestion_level
