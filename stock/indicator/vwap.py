import pandas as pd
import matplotlib.pyplot as plt
from stock.data.config import VWAP_CONFIG  # 从配置文件导入 VWAP 参数


def calculate_vwap(stock_data, strict=False):
    """
    计算成交量加权平均价格（VWAP）

    参数:
    stock_data (pd.DataFrame): 包含 'close' 和 'volume' 列的股票数据
    strict (bool): 严格模式，若为 True 则遇到 NaN 会报错，默认自动填补

    返回:
    pd.Series: VWAP 序列
    """
    stock_data = stock_data.copy()
    stock_data['close'] = pd.to_numeric(stock_data['close'], errors='coerce')
    stock_data['volume'] = pd.to_numeric(stock_data['volume'], errors='coerce')

    if strict:
        if stock_data['close'].isnull().any() or stock_data['volume'].isnull().any():
            missing = stock_data[stock_data[['close', 'volume']].isnull().any(axis=1)]
            raise ValueError(f"VWAP 计算中发现缺失数据:\n{missing}")

    # 自动填补缺失数据
    stock_data['close'] = stock_data['close'].ffill()
    stock_data['volume'] = stock_data['volume'].fillna(0)

    # 计算 VWAP = ∑(成交额) / ∑(成交量)
    cumulative_value = (stock_data['close'] * stock_data['volume']).cumsum()
    cumulative_volume = stock_data['volume'].cumsum()

    vwap = cumulative_value / cumulative_volume
    return pd.Series(vwap, index=stock_data.index)



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
             color='orange', linestyle='--', alpha=0.7, linewidth=2)

    plt.title('Stock Price and Volume Weighted Average Price (VWAP)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(loc='best', fontsize=12)
    plt.tight_layout()
    plt.show()


def generate_vwap_operation_suggestion(stock_data, vwap_data):
    """
    根据 VWAP 指标生成详细操作建议

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价
    vwap_data (pd.Series): VWAP 值

    返回:
    str: 操作建议
    """
    # 获取最新的收盘价和 VWAP 值
    latest_price = stock_data['close'].iloc[-1]
    latest_vwap = vwap_data.iloc[-1]

    # 配置文件中的买入和卖出阈值
    buy_threshold = VWAP_CONFIG.get("buy_threshold", 0.5)  # 默认值为 0.5%
    sell_threshold = VWAP_CONFIG.get("sell_threshold", -0.5)  # 默认值为 -0.5%

    # 计算价格与 VWAP 的偏离程度（百分比）
    deviation = (latest_price - latest_vwap) / latest_vwap * 100

    # 初始化操作建议
    if deviation > buy_threshold:
        suggestion = "买入"
        detailed_suggestion = (
            f"VWAP - {latest_vwap:.2f}, 当前股价 - {latest_price:.2f}，"
            f"股价高于 VWAP {deviation:.2f}%，显示市场的多头力量较强，价格有上涨潜力。\n"
            "📌建议：市场处于上涨趋势，考虑买入或继续持有，顺势而为。"
        )
    elif deviation < sell_threshold:
        suggestion = "卖出"
        detailed_suggestion = (
            f"VWAP - {latest_vwap:.2f}, 当前股价 - {latest_price:.2f}，"
            f"股价低于 VWAP {deviation:.2f}%，显示市场的空头力量较强，价格可能会下行。\n"
            "📌建议：市场处于下行趋势，考虑卖出或减仓，避免亏损。"
        )
    else:
        suggestion = "观望"
        detailed_suggestion = (
            f"VWAP - {latest_vwap:.2f}, 当前股价 - {latest_price:.2f}，"
            "价格接近 VWAP，市场方向不明，短期内难以判断趋势。\n"
            "📌建议：维持观望，等待更明确的信号出现。"
        )

    # 输出详细的操作建议
    print(detailed_suggestion)
    print("-----------------------------------------------------------------------------------------------------")

    return suggestion
