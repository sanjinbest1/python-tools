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

    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.ewm(span=window, adjust=False).mean()
    avg_loss = loss.ewm(span=window, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi = np.where(avg_loss == 0, 100, rsi)  # 防止 avg_loss 为 0 导致 NaN

    return pd.Series(rsi, index=data.index)

def calculate_rsi_for_multiple_windows(stock_data):
    """
    计算多个窗口期的 RSI 值并返回

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价
    window_list (list): RSI 窗口期列表，默认为配置文件中的窗口期

    返回:
    dict: 包含多个 RSI 序列的字典
    """
    window_list = RSI_CONFIG["window_list"]  # 读取配置中的窗口期

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
    根据多个周期的 RSI 值生成操作建议

    参数:
    rsi_values (dict): 含有多个周期 RSI 值的字典

    返回:
    str: 操作建议
    """
    latest_rsi_values = {window: rsi.iloc[-1] for window, rsi in rsi_values.items()}

    overbought = RSI_CONFIG["overbought"]
    oversold = RSI_CONFIG["oversold"]

    buy_count = sum(1 for rsi in latest_rsi_values.values() if rsi < oversold)
    sell_count = sum(1 for rsi in latest_rsi_values.values() if rsi > overbought)

    # 短期与长期趋势判断
    short_term_rsi = latest_rsi_values[min(latest_rsi_values)]
    long_term_rsi = latest_rsi_values[max(latest_rsi_values)]

    if short_term_rsi > overbought and long_term_rsi > overbought:
        sell_count += 1
    elif short_term_rsi < oversold and long_term_rsi < oversold:
        buy_count += 1

    if buy_count > sell_count:
        return "买入"
    elif sell_count > buy_count:
        return "卖出"
    return "观望"

