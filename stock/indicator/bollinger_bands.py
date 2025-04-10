import pandas as pd
import matplotlib.pyplot as plt
from stock.data.config import BOLLINGER_CONFIG  # 配置中应包含 WINDOW 和 NUM_STD


def calculate_bollinger_bands(data: pd.DataFrame) -> pd.DataFrame:
    """
    计算布林带指标（含中轨、上下轨）
    """
    window = BOLLINGER_CONFIG["WINDOW"]
    num_std = BOLLINGER_CONFIG["NUM_STD"]

    sma = data["close"].rolling(window=window).mean()
    std = data["close"].rolling(window=window).std()

    return data.assign(
        SMA=sma,
        Upper_Band=sma + num_std * std,
        Lower_Band=sma - num_std * std
    )


def generate_bollinger_signals(data: pd.DataFrame) -> pd.DataFrame:
    """
    生成布林带买卖信号（包含突破上下轨）
    """
    buy_signal = (data["close"] < data["Lower_Band"]) & (data["close"].shift(1) >= data["Lower_Band"].shift(1))
    sell_signal = (data["close"] > data["Upper_Band"]) & (data["close"].shift(1) <= data["Upper_Band"].shift(1))

    return data.assign(
        Buy_Signal=buy_signal,
        Sell_Signal=sell_signal
    )


def generate_bollinger_operations(df: pd.DataFrame) -> dict:
    """
    基于最新布林带状态生成操作建议

    参数:
    df (pd.DataFrame): 包含布林带指标的股票数据

    返回:
    dict: 包含操作建议及详细建议的字典
    """
    latest = df.iloc[-1]

    suggestion_text = f"布林带指标：当前收盘价为 {latest['close']:.2f}，下轨 {latest['Lower_Band']:.2f}，上轨 {latest['Upper_Band']:.2f}。\n"

    if latest["Buy_Signal"]:
        suggestion_text += (
            "\n价格刚刚跌破下轨，可能出现超卖反弹。\n"
            "📌 建议：关注反弹确认信号，适当低吸试探建仓，可设置小止损保护。"
        )
        suggestion_level = "买入"
        detailed_suggestion = (
            "当前价格刚刚跌破布林带下轨，市场可能处于超卖状态，存在反弹机会。建议观察反弹信号，"
            "适量低吸试探建仓，并设置小止损来规避市场波动风险。"
        )
    elif latest["Sell_Signal"]:
        suggestion_text += (
            "\n价格刚刚突破上轨，可能为短期超买。\n"
            "📌 建议：关注回调信号或滞涨迹象，可逢高减仓或落袋为安。"
        )
        suggestion_level = "卖出"
        detailed_suggestion = (
            "当前价格突破布林带上轨，市场可能处于超买状态，存在回调风险。建议密切关注回调信号，"
            "或在滞涨迹象出现时逢高减仓或止盈。"
        )
    else:
        suggestion_text += (
            "\n价格位于布林带中轨之间，市场波动有限，方向尚不明确。\n"
            "📌 建议：继续观望，待价格突破上下轨或配合其他指标判断。"
        )
        suggestion_level = "观望"
        detailed_suggestion = (
            "当前价格位于布林带中轨之间，市场波动较小，方向尚不明确。建议保持观望，"
            "待价格突破布林带上下轨时再作进一步决策，或者结合其他指标来确认入场时机。"
        )

    # 返回包含建议和详细建议的字典
    return {
        "suggestion": suggestion_level,
        "detailed_suggestion": detailed_suggestion
    }



def plot_bollinger_bands(data: pd.DataFrame):
    """
    绘制布林带与买卖信号图
    """
    plt.figure(figsize=(14, 7))
    plt.plot(data["close"], label="Close", color="black", lw=1)
    plt.plot(data["SMA"], label=f"SMA ({BOLLINGER_CONFIG['WINDOW']})", color="orange", lw=1.2)
    plt.plot(data["Upper_Band"], label="Upper Band", color="red", linestyle="--")
    plt.plot(data["Lower_Band"], label="Lower Band", color="green", linestyle="--")

    # 信号标记
    plt.scatter(data.index[data["Buy_Signal"]], data["close"][data["Buy_Signal"]],
                marker="^", color="green", label="Buy Signal", s=100)
    plt.scatter(data.index[data["Sell_Signal"]], data["close"][data["Sell_Signal"]],
                marker="v", color="red", label="Sell Signal", s=100)

    plt.title("📈 Bollinger Bands with Buy/Sell Signals", fontsize=16)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
