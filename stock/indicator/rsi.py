import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_rsi_for_multiple_windows(stock_data, window_list):
    """
    计算多个窗口期的RSI值并返回
    :param stock_data: 股票数据，包含收盘价
    :param window_list: RSI窗口期列表
    :return: 一个包含多个 RSI 序列的字典
    """
    rsi_values = {}
    for window in window_list:
        rsi_values[window] = calculate_rsi(stock_data['close'], window)
    return rsi_values


def plot_multiple_rsi(stock_data, rsi_values, window_list):
    """
    绘制多个周期的 RSI 图表，同时显示不同周期的 RSI 指标
    :param stock_data: 股票数据，包含收盘价
    :param rsi_values: 各个周期的 RSI 值（字典形式）
    :param window_list: RSI 窗口期列表
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 绘制股票收盘价图
    ax1.plot(stock_data.index, stock_data['close'], label='Stock Price', color='blue')
    ax1.set_title(f'Stock Price and RSI ({", ".join([str(w) + "-day" for w in window_list])})', fontsize=14)
    ax1.set_ylabel('Stock Price', color='blue')
    ax1.set_xlabel('Date')
    ax1.legend(loc='upper left')

    # 创建共享x轴的第二个坐标轴用于绘制多个RSI
    ax2 = ax1.twinx()

    # 逐个绘制每个周期的 RSI
    colors = ['orange', 'green', 'red', 'purple']
    for i, window in enumerate(window_list):
        ax2.plot(rsi_values[window].index, rsi_values[window], label=f'RSI ({window}-day)', color=colors[i % len(colors)])

    # 添加超买和超卖参考线
    ax2.axhline(y=75, color='r', linestyle='--', label='Overbought (75)')
    ax2.axhline(y=25, color='g', linestyle='--', label='Oversold (25)')
    ax2.set_ylabel('RSI', color='orange')
    ax2.legend(loc='upper right')

    # 调整布局，防止子图重叠
    plt.tight_layout()
    plt.show()

def calculate_rsi(data, window=14):
    """
    计算RSI（相对强弱指数）

    参数:
    data (pd.Series): 股票的收盘价序列
    window (int): RSI计算的窗口期，默认为14

    返回:
    pd.Series: RSI值
    """
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # **使用指数加权移动平均 (EMA)**
    avg_gain = gain.ewm(span=window, adjust=False).mean()
    avg_loss = loss.ewm(span=window, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # **防止 avg_loss 为 0 导致 NaN**
    rsi = np.where(avg_loss == 0, 100, rsi)

    return pd.Series(rsi, index=data.index)

def generate_operation_suggestion(rsi_values, window_list):
    """
    根据多个周期的 RSI 值生成操作建议

    参数:
    rsi_values (dict): 含有多个周期 RSI 值的字典
    window_list (list): RSI 窗口期列表
    stock_data (pd.DataFrame): 股票数据

    返回:
    str: 操作建议
    """
    latest_rsi_values = {window: rsi_values[window].iloc[-1] for window in window_list}

    overbought = 75
    oversold = 25

    # 操作建议
    suggestions = []

    # 分析每个周期的 RSI 并给出建议
    for window, rsi in latest_rsi_values.items():
        if rsi > overbought:
            suggestions.append(f"RSI ({window}-day): 超买，建议卖出或减仓")
        elif rsi < oversold:
            suggestions.append(f"RSI ({window}-day): 超卖，建议买入或加仓")
        else:
            suggestions.append(f"RSI ({window}-day): 正常区间，建议持有")

    # 判断是否短期和长期 RSI 一致
    if latest_rsi_values[window_list[0]] > overbought and latest_rsi_values[window_list[-1]] > overbought:
        suggestions.append("短期和长期均超买，市场可能回调，建议卖出或减仓")
    elif latest_rsi_values[window_list[0]] < oversold and latest_rsi_values[window_list[-1]] < oversold:
        suggestions.append("短期和长期均超卖，市场可能反弹，建议买入或加仓")

    # 汇总操作建议
    return "\n".join(suggestions)


