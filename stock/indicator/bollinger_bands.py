import pandas as pd
import matplotlib.pyplot as plt


def calculate_bollinger_bands(data, window=20, num_std=2):
    """
    计算布林带指标

    参数:
    data (pd.DataFrame): 包含收盘价的DataFrame
    window (int): 计算移动平均线和标准差的窗口大小，默认为20
    num_std (int): 标准差的倍数，默认为2

    返回:
    pd.DataFrame: 包含布林带指标的DataFrame
    """
    # 使用loc方法明确指定修改位置
    data.loc[:, 'SMA'] = data['close'].rolling(window=window).mean()
    data.loc[:, 'std'] = data['close'].rolling(window=window).std()

    data.loc[:, 'Upper_Band'] = data['SMA'] + (data['std'] * num_std)
    data.loc[:, 'Lower_Band'] = data['SMA'] - (data['std'] * num_std)

    return data


def generate_bollinger_signals(data):
    """
    生成布林带买卖信号

    参数:
    data (pd.DataFrame): 包含布林带指标的DataFrame

    返回:
    pd.DataFrame: 包含布林带买卖信号的DataFrame
    """
    #使用loc方法明确指定修改位置
    data.loc[:, 'Buy_Signal'] = (data['close'] < data['Lower_Band'])
    data.loc[:, 'Sell_Signal'] = (data['close'] > data['Upper_Band'])

    return data

def generate_bollinger_operations(df):
    """
    根据布林带信号生成操作建议（中文版本）
    :param df: 包含布林带和信号的DataFrame
    :return: 操作建议（字符串）
    """
    latest_data = df.iloc[-1]  # 获取最新一条数据

    # 初始化操作建议
    simple_operation = "观望"
    detailed_operation = "收盘价 - {:.2f}, 下轨 - {:.2f}, 上轨 - {:.2f}, 观望：当前价格位于布林带区间内，暂无明显买卖信号。".format(latest_data['close'], latest_data['Lower_Band'], latest_data['Upper_Band'])

    if latest_data['close'] < latest_data['Lower_Band']:
        detailed_operation = "收盘价 - {:.2f}, 下轨 - {:.2f}, 上轨 - {:.2f}, 买入：当前价格低于布林带下轨，可能存在超卖，建议关注买入机会。".format(latest_data['close'], latest_data['Lower_Band'], latest_data['Upper_Band'])
        simple_operation = "买入"
    elif latest_data['close'] > latest_data['Upper_Band']:
        detailed_operation = "收盘价 - {:.2f}, 下轨 - {:.2f}, 上轨 - {:.2f}, 卖出：当前价格高于布林带上轨，可能存在超买，建议关注卖出机会。".format(latest_data['close'], latest_data['Lower_Band'], latest_data['Upper_Band'])
        simple_operation = "卖出"

    print(detailed_operation)
    return simple_operation



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
