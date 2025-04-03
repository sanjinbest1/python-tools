import pandas as pd
import matplotlib.pyplot as plt
from stock.data.config import VWAP_CONFIG  # 从配置文件导入 VWAP 参数


def calculate_vwap(stock_data):
    """
    计算成交量加权移动平均（VWAP）指标

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价和成交量

    返回:
    pd.Series: VWAP值
    """
    stock_data['close'] = pd.to_numeric(stock_data['close'], errors='coerce')
    stock_data['volume'] = pd.to_numeric(stock_data['volume'], errors='coerce')

    # 计算 VWAP
    numerator = (stock_data['close'] * stock_data['volume']).cumsum()
    denominator = stock_data['volume'].cumsum()
    vwap = numerator / denominator

    return vwap


def plot_vwap(stock_data, vwap_data):
    """
    绘制包含股价和 VWAP 的图表

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价
    vwap_data (pd.Series): VWAP 值
    """
    plt.figure(figsize=(12, 8))

    # 绘制股票收盘价图
    plt.plot(stock_data.index, stock_data['close'], label='Stock Price',
             color='blue', alpha=0.6, linewidth=1)

    # 绘制 VWAP 图
    plt.plot(vwap_data.index, vwap_data, label='VWAP',
             color='orange', linestyle='--', alpha=0.7, linewidth=1)

    plt.title('Stock Price and Volume Weighted Average Price (VWAP)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(loc='best', fontsize=12)
    plt.tight_layout()
    plt.show()

def generate_vwap_operation_suggestion(stock_data, vwap_data):
    """
    根据 VWAP 指标生成操作建议

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价
    vwap_data (pd.Series): VWAP 值

    返回:
    str: 操作建议
    """
    latest_price = stock_data['close'].iloc[-1]
    latest_vwap = vwap_data.iloc[-1]

    buy_threshold = VWAP_CONFIG["buy_threshold"]
    sell_threshold = VWAP_CONFIG["sell_threshold"]

    # 计算价格与 VWAP 的偏离程度
    deviation = (latest_price - latest_vwap) / latest_vwap * 100

    # 生成操作建议
    if deviation > buy_threshold:
        suggestion = "买入"
        detail = f"VWAP - {latest_vwap:.2f}, 当前股价 - {latest_price:.2f}，股价高于 VWAP {deviation:.2f}%，多头力量较强，建议买入或持有。"
    elif deviation < sell_threshold:
        suggestion = "卖出"
        detail = f"VWAP - {latest_vwap:.2f}, 当前股价 - {latest_price:.2f}，股价低于 VWAP {deviation:.2f}%，空头力量较强，建议卖出或观望。"
    else:
        suggestion = "观望"
        detail = f"VWAP - {latest_vwap:.2f}, 当前股价 - {latest_price:.2f}，市场方向不明，建议观望。"

    print(detail)
    return suggestion
