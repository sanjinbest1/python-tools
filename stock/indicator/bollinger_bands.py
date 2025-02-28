import pandas as pd
import matplotlib.pyplot as plt

def calculate_bollinger_bands(data, window=20, num_std=2):
    """
    计算布林带：中间线（SMA）、上轨线、下轨线
    :param data: 包含股票历史数据的DataFrame，要求至少有 'close' 列
    :param window: 移动平均线的窗口大小，默认20
    :param num_std: 标准差倍数，默认2
    :return: 返回带有布林带的DataFrame
    """
    data['SMA'] = data['close'].rolling(window=window).mean()  # 计算20日简单移动平均线
    data['std'] = data['close'].rolling(window=window).std()  # 计算20日标准差

    # 计算布林带的上下轨
    data['Upper_Band'] = data['SMA'] + (data['std'] * num_std)
    data['Lower_Band'] = data['SMA'] - (data['std'] * num_std)

    return data

def generate_bollinger_signals(data):
    """
    根据布林带生成买入卖出信号
    :param data: 包含布林带数据的DataFrame
    :return: 添加了 'Buy_Signal' 和 'Sell_Signal' 的DataFrame
    """
    data['Buy_Signal'] = (data['close'] < data['Lower_Band'])  # 当收盘价低于下轨时买入
    data['Sell_Signal'] = (data['close'] > data['Upper_Band'])  # 当收盘价高于上轨时卖出

    return data


def generate_bollinger_operations(df):
    """
    根据布林带信号生成操作建议
    :param df: 包含布林带和信号的DataFrame
    :return: 操作建议（字符串）
    """
    latest_data = df.iloc[-1]  # 获取最新一条数据

    # 初始化操作建议
    operation = "No action"

    if latest_data['close'] < latest_data['Lower_Band']:
        operation = "Buy: The price is below the lower Bollinger Band, suggesting a potential buying opportunity."
    elif latest_data['close'] > latest_data['Upper_Band']:
        operation = "Sell: The price is above the upper Bollinger Band, suggesting a potential selling opportunity."
    else:
        operation = "Hold: The price is within the Bollinger Bands, suggesting no immediate action."

    return operation


def plot_bollinger_bands(data):
    """
    绘制布林带图表（包括收盘价、中轨线、上轨线、下轨线以及买入卖出信号）
    :param data: 包含布林带及信号的DataFrame
    """
    plt.figure(figsize=(12, 8))  # 设置图表尺寸

    # 绘制收盘价
    plt.plot(data['close'], label='close Price', color='blue', alpha=0.6, linewidth=1)

    # 绘制20日简单移动平均线
    plt.plot(data['SMA'], label='SMA (20)', color='orange', alpha=0.7, linestyle='-', linewidth=1)

    # 绘制布林带上轨线
    plt.plot(data['Upper_Band'], label='Upper Band', color='red', linestyle='--', alpha=0.6, linewidth=1)

    # 绘制布林带下轨线
    plt.plot(data['Lower_Band'], label='Lower Band', color='green', linestyle='--', alpha=0.6, linewidth=1)

    # 绘制买入信号（收盘价低于下轨线时）
    plt.scatter(data.index[data['Buy_Signal']], data['close'][data['Buy_Signal']], label='Buy Signal', marker='^', color='g', alpha=1, s=100)

    # 绘制卖出信号（收盘价高于上轨线时）
    plt.scatter(data.index[data['Sell_Signal']], data['close'][data['Sell_Signal']], label='Sell Signal', marker='v', color='r', alpha=1, s=100)

    # 设置图表标题
    plt.title('Bollinger Bands with Buy/Sell Signals', fontsize=16)

    # 设置X轴和Y轴标签
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)

    # 设置X轴刻度格式（日期显示更友好）
    plt.xticks(rotation=45)

    # 添加图例
    plt.legend(loc='best', fontsize=12)

    # 显示图表
    plt.tight_layout()  # 自动调整布局，避免图表元素重叠
    plt.show()
