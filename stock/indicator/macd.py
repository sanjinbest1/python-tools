import pandas as pd
import matplotlib.pyplot as plt
from stock.data.config import MACD_CONFIG


def calculate_macd(data):
    """
    计算 MACD 指标
    """
    if not isinstance(data, pd.Series):
        raise ValueError("data 必须为 pd.Series 类型")

    fast = MACD_CONFIG["fast_period"]
    slow = MACD_CONFIG["slow_period"]
    signal = MACD_CONFIG["signal_period"]

    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()

    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line

    return macd,signal_line,hist


def generate_macd_signal(macd, signal, hist):
    """
    根据 MACD 和 Signal 生成更详细的交易建议

    参数:
    macd (pd.Series): MACD 指标数据
    signal (pd.Series): Signal 指标数据
    hist (pd.Series): MACD 的柱状图数据 (暂时未使用，可根据需要扩展)

    返回:
    dict: 包含操作建议、解释、策略和风险提示的字典
    """
    if not isinstance(macd, pd.Series): macd = pd.Series(macd)
    if not isinstance(signal, pd.Series): signal = pd.Series(signal)

    if len(macd) < 2 or len(signal) < 2:
        print("MACD 或 Signal 数据不足，返回'观望'")
        return {
            "suggestion": "观望",
            "detailed_suggestion": "MACD 或 Signal 数据不足，无法生成建议。"
        }

    macd = pd.to_numeric(macd, errors='coerce')
    signal = pd.to_numeric(signal, errors='coerce')

    if macd.isna().any() or signal.isna().any():
        print("MACD 或 Signal 存在 NaN 值，返回'观望'")
        return {
            "suggestion": "观望",
            "detailed_suggestion": "MACD 或 Signal 存在 NaN 值，无法生成建议。"
        }

    latest_macd = macd.iloc[-1]
    prev_macd = macd.iloc[-2]
    latest_signal = signal.iloc[-1]
    prev_signal = signal.iloc[-2]

    buy_signal = latest_macd > latest_signal and prev_macd <= prev_signal
    sell_signal = latest_macd < latest_signal and prev_macd >= prev_signal

    if buy_signal:
        suggestion = "买入"
        explanation = "MACD 向上突破 Signal 线，形成“黄金交叉”，通常被视为上涨信号。"
        strategy = (
            "- 可在当前价格小仓位试探性建仓，若后续价格继续上行可加仓。\n"
            "- 可结合成交量或布林带突破确认强势上涨。"
        )
        risk = (
            "- 若价格回踩黄金交叉位置或MA支撑位失守，应果断止损。\n"
            "- 设置止损线建议为入场价下方 3%-5%。"
        )
    elif sell_signal:
        suggestion = "卖出"
        explanation = "MACD 向下跌破 Signal 线，形成“死亡交叉”，通常被视为下跌预警信号。"
        strategy = (
            "- 考虑减仓或平仓，防止利润回吐或亏损扩大。\n"
            "- 如有空头策略，可尝试布局做空。"
        )
        risk = (
            "- 若信号为假突破，可设置回补止损线。\n"
            "- 避免在强支撑位盲目追空。"
        )
    elif latest_macd < 0:
        suggestion = "卖出"
        explanation = "MACD 位于零轴下方，表示整体市场偏弱。"
        strategy = (
            "- 若已持有股票，应考虑减仓或等待反弹卖出。\n"
            "- 不建议在该位置轻易抄底，除非有其他强支撑。"
        )
        risk = (
            "- 空头趋势中反弹较弱，建议轻仓谨慎操作。\n"
            "- 止损线应设置在前期低点或5%以内。"
        )
    else:
        suggestion = "观望"
        explanation = "MACD 虽然在零轴上方，但未出现明显交叉信号。趋势尚不明朗。"
        strategy = (
            "- 建议持仓者继续持有，关注后续是否出现明确交叉。\n"
            "- 若股价沿趋势缓慢上涨，可小仓位跟进。"
        )
        risk = (
            "- 缺乏量能配合的上涨信号可靠性差。\n"
            "- 注意回调信号，设置动态止盈。"
        )

    # 返回包含操作建议、解释、策略和风险提示的字典
    return {
        "suggestion": suggestion,
        "detailed_suggestion": f"信号解释：{explanation}\n策略建议：\n{strategy}\n风险提示：\n{risk}"
    }




def plot_macd_with_signal(price, macd_dict, time_period=None):
    """
    绘制 MACD 图表
    """
    if time_period:
        price = price.tail(time_period)
        for key in macd_dict:
            macd_dict[key] = macd_dict[key].tail(time_period)

    plt.figure(figsize=(12, 8))

    # 价格图
    plt.subplot(3, 1, 1)
    plt.plot(price.index, price, label='Price', color='blue')
    plt.title("Stock Price")
    plt.legend()

    # MACD 图
    plt.subplot(3, 1, 2)
    plt.plot(macd_dict['macd'].index, macd_dict['macd'], label='MACD', color='purple')
    plt.plot(macd_dict['signal'].index, macd_dict['signal'], label='Signal', linestyle='--', color='orange')
    plt.bar(macd_dict['hist'].index, macd_dict['hist'], label='Histogram', color='gray', alpha=0.4)

    # 高亮最新交叉信号
    macd = macd_dict["macd"]
    signal = macd_dict["signal"]
    color = "gray"
    if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
        color = "green"
    elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
        color = "red"

    plt.scatter(macd.index[-1], macd.iloc[-1], color=color, s=100, label='Latest Signal')
    plt.title("MACD Indicator")
    plt.legend()

    plt.tight_layout()
    plt.show()

    return generate_macd_signal(macd, signal)


# 示例运行
if __name__ == "__main__":
    dates = pd.date_range(start="2024-01-01", periods=100, freq='D')
    prices = pd.Series([100 + i + (i % 5) * 2 for i in range(100)], index=dates)

    macd_data = calculate_macd(prices)
    signal = plot_macd_with_signal(prices, macd_data)
