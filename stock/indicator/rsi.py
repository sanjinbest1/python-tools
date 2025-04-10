import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from stock.data.config import RSI_CONFIG  # 从配置文件导入 RSI 参数

def calculate_rsi(data, window=None):
    """
    计算 RSI（相对强弱指数）

    参数:
    data (pd.Series): 股票的收盘价序列
    window (int): RSI 计算窗口期，默认为配置文件中的值

    返回:
    pd.Series: RSI 值
    """
    if window is None:
        window = RSI_CONFIG["default_window"]  # 读取默认 RSI 窗口期

    # 检查输入数据的完整性
    if data.isnull().any():
        raise ValueError("输入的股票数据包含缺失值，请清理数据。")

    delta = data.diff()
    gain = np.maximum(delta, 0)  # gain 可以直接通过向量化的最大值运算获得
    loss = np.maximum(-delta, 0)  # loss 可以直接通过向量化的最大值运算获得

    avg_gain = gain.ewm(span=window, adjust=False).mean()
    avg_loss = loss.ewm(span=window, adjust=False).mean()

    # 避免除以零
    rs = avg_gain / (avg_loss + 1e-10)  # 加一个小的正数避免除零
    rsi = 100 - (100 / (1 + rs))

    return pd.Series(rsi, index=data.index)

def calculate_rsi_for_multiple_windows(stock_data):
    """
    计算多个窗口期的 RSI 值并返回

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价

    返回:
    dict: 包含多个 RSI 序列的字典
    """
    window_list = RSI_CONFIG.get("window_list", [6, 14, 24])  # 读取配置中的窗口期
    if not window_list:
        raise ValueError("配置文件中未定义 RSI 窗口期列表。")

    return {window: calculate_rsi(stock_data['close'], window) for window in window_list}

def plot_multiple_rsi(stock_data, rsi_values):
    """
    绘制多个周期的 RSI 图表

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价
    rsi_values (dict): 各个周期的 RSI 值（字典形式）
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(stock_data.index, stock_data['close'], label='Stock Price', color='blue')
    ax1.set_title('Stock Price and RSI', fontsize=14)
    ax1.set_ylabel('Stock Price', color='blue')
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    colors = ['orange', 'green', 'red', 'purple']

    for i, (window, rsi) in enumerate(rsi_values.items()):
        ax2.plot(rsi.index, rsi, label=f'RSI ({window}-day)', color=colors[i % len(colors)])

    ax2.axhline(y=RSI_CONFIG["overbought"], color='r', linestyle='--', label='Overbought')
    ax2.axhline(y=RSI_CONFIG["oversold"], color='g', linestyle='--', label='Oversold')
    ax2.set_ylabel('RSI', color='orange')
    ax2.legend(loc='upper right')

    plt.tight_layout()
    plt.show()

def generate_operation_suggestion(rsi_values):
    """
    根据多个周期的 RSI 值生成操作建议，并附带详细说明

    参数:
    rsi_values (dict): 含有多个周期 RSI 值的字典（例如 {6: Series, 14: Series, 24: Series}）

    返回:
    dict: 包含操作建议和详细建议的字典
    """
    latest_rsi_values = {window: rsi.iloc[-1] for window, rsi in rsi_values.items()}
    overbought = RSI_CONFIG["overbought"]
    oversold = RSI_CONFIG["oversold"]

    # 统计超买和超卖的周期数
    buy_count = sum(1 for v in latest_rsi_values.values() if v < oversold)
    sell_count = sum(1 for v in latest_rsi_values.values() if v > overbought)

    # 趋势增强判断
    short_rsi = min(latest_rsi_values.values())
    long_rsi = max(latest_rsi_values.values())

    if short_rsi < oversold and long_rsi < oversold:
        buy_count += 1
    elif short_rsi > overbought and long_rsi > overbought:
        sell_count += 1

    # 文案构建
    detail = "RSI - 当前各周期 RSI 指数如下：\n"
    for window, value in sorted(latest_rsi_values.items()):
        detail += f"- {window} 日 RSI：{value:.2f}  "

    # 操作建议构建
    result = '观望'
    if buy_count > sell_count:
        suggestion = (
            f"RSI - 综合判断：多个周期 RSI 值均低于超卖区间，且短期与长期走势均显示超卖，"
            "市场可能出现反弹，📌 建议【买入】。根据当前的超卖信号，"
            "您可以考虑趁市场低迷时买入，但需警惕短期的震荡风险。"
        )
        result = '买入'
    elif sell_count > buy_count:
        suggestion = (
            f"RSI - 综合判断：多个周期 RSI 值均高于超买区间，且短期与长期走势均显示超买，"
            "市场可能面临回调，📌 建议【卖出】。当前市场可能处于过度上涨状态，"
            "若您持有股票，考虑适时卖出以锁定收益，避免回调风险。"
        )
        result = '卖出'
    else:
        suggestion = (
            f"RSI - 综合判断：各周期 RSI 指标未明显偏离常态，当前短期与长期走势保持中性，"
            "市场缺乏明确的超买或超卖信号，📌 建议【观望】。此时宜保持观望，等待市场进一步明朗。"
        )

    # 返回包含操作建议和详细建议的字典
    return {
        "suggestion": result,
        "detailed_suggestion": suggestion
    }

