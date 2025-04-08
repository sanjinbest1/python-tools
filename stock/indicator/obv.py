import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from stock.data.config import OBV_CONFIG  # 从配置文件导入参数

def calculate_obv(stock_data, initial_value=None, strict=False):
    """
    计算能量潮（OBV）指标

    参数:
    stock_data (pd.DataFrame): 股票数据，包含 'close' 和 'volume' 列
    initial_value (float): OBV 初始值（默认读取配置）
    strict (bool): 是否严格校验缺失数据，默认 False 为自动填补

    返回:
    pd.Series: OBV 序列
    """

    if initial_value is None:
        initial_value = OBV_CONFIG.get("obv_initial_value", 0)

    # 检查关键列是否存在
    required_cols = ['close', 'volume']
    for col in required_cols:
        if col not in stock_data.columns:
            raise ValueError(f"数据中缺失必要列: {col}")

    # 严格模式下报错退出
    if strict:
        if stock_data['close'].isnull().any() or stock_data['volume'].isnull().any():
            missing = stock_data[stock_data[['close', 'volume']].isnull().any(axis=1)]
            raise ValueError(f"数据存在缺失值:\n{missing}")

    # 自动填补缺失值
    stock_data = stock_data.copy()
    stock_data['close'] = stock_data['close'].ffill()
    stock_data['volume'] = stock_data['volume'].fillna(0)

    # 收盘价变化（向后差）
    delta = stock_data['close'].diff()

    # OBV 逻辑向量化处理：上涨加量，下跌减量，持平不变
    obv_change = np.where(delta > 0, stock_data['volume'],
                          np.where(delta < 0, -stock_data['volume'], 0))

    obv = np.cumsum(obv_change) + initial_value

    return pd.Series(obv, index=stock_data.index)


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
    根据 OBV 指标生成详细操作建议

    参数:
    obv_data (pd.Series): OBV 值序列
    stock_data (pd.DataFrame): 股票数据，包含收盘价

    返回:
    str: 操作建议
    """
    # OBV 和收盘价的变化趋势
    obv_trend = obv_data.diff().iloc[-1]
    price_trend = stock_data['close'].diff().iloc[-1]

    # OBV 配置参数
    threshold_positive = OBV_CONFIG["obv_threshold_positive"]
    threshold_negative = OBV_CONFIG["obv_threshold_negative"]

    # 默认操作建议
    detailed_suggestion = "无建议，观望"
    simple_suggestion = "观望"

    # 如果 OBV 增加且股价也上涨
    if obv_trend > threshold_positive and price_trend > 0:
        detailed_suggestion = (
            f"OBV - {obv_trend:.2f}, 收盘价变化 - {price_trend:.2f}, "
            "OBV 上升且股价上涨，显示市场的多头力量强劲，继续上涨的可能性较大。\n"
            "📌 建议：市场向好，建议【买入】或持有当前仓位，顺势而为。"
        )
        simple_suggestion = "买入"

    # 如果 OBV 增加但股价下跌
    elif obv_trend > threshold_positive and price_trend < 0:
        detailed_suggestion = (
            f"OBV - {obv_trend:.2f}, 收盘价变化 - {price_trend:.2f}, "
            "虽然 OBV 增加，但股价下跌，可能是短期回调或震荡区间的形成。\n"
            "📌 建议：注意价格回调，可能是买入机会，但建议保持谨慎。"
        )
        simple_suggestion = "买入"

    # 如果 OBV 下降且股价上涨
    elif obv_trend < threshold_negative and price_trend > 0:
        detailed_suggestion = (
            f"OBV - {obv_trend:.2f}, 收盘价变化 - {price_trend:.2f}, "
            "OBV 下降但股价上涨，市场的多头动能不足，可能是伪突破。\n"
            "📌 建议：市场动能减弱，建议【卖出】或保持观望，避免追高。"
        )
        simple_suggestion = "卖出"

    # 如果 OBV 下降且股价下跌
    elif obv_trend < threshold_negative and price_trend < 0:
        detailed_suggestion = (
            f"OBV - {obv_trend:.2f}, 收盘价变化 - {price_trend:.2f}, "
            "OBV 和股价都在下降，表明市场空头力量较强，可能出现持续下行。\n"
            "📌 建议：市场空头趋势明显，建议【卖出】或保持观望，避免持仓。"
        )
        simple_suggestion = "卖出"

    # 输出详细的操作建议
    print(detailed_suggestion)
    print("-----------------------------------------------------------------------------------------------------")
    return simple_suggestion
