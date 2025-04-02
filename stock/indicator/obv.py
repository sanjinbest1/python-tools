import pandas as pd
import matplotlib.pyplot as plt


def calculate_obv(stock_data):
    """
    计算能量潮（OBV）指标

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价和成交量

    返回:
    pd.Series: OBV值
    """
    delta = stock_data['close'].diff()
    volume = pd.to_numeric(stock_data['volume'], errors='coerce')  # 将volume列转换为数值类型

    obv = []
    obv.append(float(volume.iloc[0]))  # 将初始值转换为浮点数类型
    for i in range(1, len(delta)):
        if delta.iloc[i] > 0:
            obv.append(obv[-1] + volume.iloc[i])
        elif delta.iloc[i] < 0:
            obv.append(obv[-1] - volume.iloc[i])
        else:
            obv.append(obv[-1])

    obv_series = pd.Series(obv, index=stock_data.index)
    return obv_series


def plot_obv(stock_data, obv_data):
    """
    绘制 OBV 图表

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价
    obv_data (pd.Series): OBV 值
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # 绘制股票收盘价图
    ax1.plot(stock_data.index, stock_data['close'], label='Stock Price', color='blue')
    ax1.set_title('Stock Price', fontsize=14)
    ax1.set_ylabel('Stock Price', color='blue')
    ax1.legend(loc='upper left')

    # 绘制 OBV 图
    ax2.plot(obv_data.index, obv_data, label='OBV', color='green')
    ax2.set_title('On Balance Volume (OBV)', fontsize=14)
    ax2.set_ylabel('OBV', color='green')
    ax2.legend(loc='upper left')

    plt.tight_layout()
    plt.show()


def generate_obv_operation_suggestion(obv_data, stock_data):
    """
    根据 OBV 指标生成操作建议

    参数:
    obv_data (pd.Series): OBV 值
    stock_data (pd.DataFrame): 股票数据，包含收盘价

    返回:
    str: 操作建议
    """
    obv_trend = obv_data.diff().iloc[-1]
    price_trend = stock_data['close'].diff().iloc[-1]

    simple_suggestion = "观望"
    if obv_trend > 0 and price_trend > 0:
        detailed_suggestion = "OBV - {:.2f}, 收盘价变化 - {:.2f}, 市场多头力量强劲，建议买入或持有。".format(obv_trend, price_trend)
        simple_suggestion = "买入"
    elif obv_trend > 0 and price_trend < 0:
        detailed_suggestion = "OBV - {:.2f}, 收盘价变化 - {:.2f}, OBV上升但股价下降，可能是短期回调，建议关注，可能是买入机会。".format(obv_trend, price_trend)
        simple_suggestion = "买入"
    elif obv_trend < 0 and price_trend > 0:
        detailed_suggestion = "OBV - {:.2f}, 收盘价变化 - {:.2f}, OBV下降但股价上升，市场动能不足，建议谨慎，可能是卖出信号。".format(obv_trend, price_trend)
        simple_suggestion = "卖出"
    elif obv_trend < 0 and price_trend < 0:
        detailed_suggestion = "OBV - {:.2f}, 收盘价变化 - {:.2f}, 市场空头力量较强，建议卖出或观望。".format(obv_trend, price_trend)
        simple_suggestion = "卖出"

    print(detailed_suggestion)
    return simple_suggestion
