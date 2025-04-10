import pandas as pd
import matplotlib.pyplot as plt
from stock.data.config import KELTNER_CONFIG  # 从配置文件导入参数


def calculate_keltner_channel(stock_data):
    """
    计算 Keltner Channel（KC 通道）

    参数:
    stock_data (pd.DataFrame): 股票数据，包含 high, low, close 列

    返回:
    pd.DataFrame: 含中轨、上轨、下轨列的 DataFrame
    """
    period = KELTNER_CONFIG["PERIOD"]
    multiplier = KELTNER_CONFIG["MULTIPLIER"]

    df = stock_data.copy()
    df["high"] = pd.to_numeric(df["high"], errors='coerce')
    df["low"] = pd.to_numeric(df["low"], errors='coerce')
    df["close"] = pd.to_numeric(df["close"], errors='coerce')

    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    ema = typical_price.ewm(span=period, adjust=False).mean()
    atr = (df["high"] - df["low"]).abs().rolling(window=period).mean()

    df["Middle_Band"] = ema
    df["Upper_Band"] = ema + multiplier * atr
    df["Lower_Band"] = ema - multiplier * atr

    return df


def generate_keltner_channel_operation_suggestion(kc_df):
    """
    根据 Keltner Channel (KC) 数据生成操作建议

    参数:
    kc_df (pd.DataFrame): 包含收盘价与 KC 三线的 DataFrame

    返回:
    dict: 包含操作建议及详细建议的字典
    """
    latest_row = kc_df.iloc[-1]

    close = latest_row["close"]
    upper = latest_row["Upper_Band"]
    lower = latest_row["Lower_Band"]

    suggestion_text = f"Keltner Channel - 当前收盘价: {close:.2f}, 上轨: {upper:.2f}, 下轨: {lower:.2f}，"

    if close > upper:
        suggestion_text += (
            "\n\n收盘价突破上轨，可能存在超买，📌 建议：\n"
            "  - 【卖出】或【减仓】，注意利润保护\n"
            "  - 设置止损防止回调风险"
        )
        suggestion_level = "卖出"
        detailed_suggestion = (
            "当前收盘价突破上轨，表明市场可能处于超买状态。建议适时卖出或减仓，"
            "同时注意止盈并设置止损以防市场回调。"
        )
    elif close < lower:
        suggestion_text += (
            "\n\n收盘价跌破下轨，可能存在超卖，📌 建议：\n"
            "  - 【买入】或【加仓】，但注意确认反弹\n"
            "  - 设置止损防趋势下行"
        )
        suggestion_level = "买入"
        detailed_suggestion = (
            "当前收盘价突破下轨，表明市场可能处于超卖状态。建议考虑买入或加仓，"
            "但务必确认反弹信号，设置止损以防趋势进一步下行。"
        )
    else:
        suggestion_text += (
            "\n\n收盘价位于通道中轨之间，趋势不明朗，📌 建议：\n"
            "  - 【观望】，等待方向突破或结合其他指标"
        )
        suggestion_level = "观望"
        detailed_suggestion = (
            "当前市场处于横盘整理状态，收盘价位于中轨附近，趋势不明朗。"
            "建议观望，等待价格突破通道的上下轨或结合其他指标进行操作。"
        )

    # 返回包含建议和详细建议的字典
    return {
        "suggestion": suggestion_level,
        "detailed_suggestion": detailed_suggestion
    }



def plot_keltner_channel(kc_df):
    """
    绘制 KC 通道图

    参数:
    kc_df (pd.DataFrame): 含 close 和 KC 三轨道的 DataFrame
    """
    plt.figure(figsize=(12, 8))
    plt.plot(kc_df.index, kc_df["close"], label='Close Price', color='blue', linewidth=1)
    plt.plot(kc_df.index, kc_df["Middle_Band"], label='Middle Band', color='orange', linewidth=1)
    plt.plot(kc_df.index, kc_df["Upper_Band"], label='Upper Band', color='red', linestyle='--')
    plt.plot(kc_df.index, kc_df["Lower_Band"], label='Lower Band', color='green', linestyle='--')

    # 高亮最后一个信号点
    latest = kc_df.iloc[-1]
    color = 'g' if latest["close"] < latest["Lower_Band"] else ('r' if latest["close"] > latest["Upper_Band"] else 'gray')
    plt.scatter(kc_df.index[-1], latest["close"], color=color, s=100, label='Latest Signal')

    plt.title('Keltner Channel with Signal', fontsize=14)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
