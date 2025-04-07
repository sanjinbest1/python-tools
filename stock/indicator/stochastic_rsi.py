import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from stock.data.config import STOCHASTIC_RSI  # 直接从配置文件导入参数

def calculate_stochastic_rsi(stock_data):
    """
    计算随机 RSI（Stochastic RSI）

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价

    返回:
    pd.DataFrame: 包含 %K 和 %D 的 DataFrame
    """
    # 从配置文件读取参数
    k_period = STOCHASTIC_RSI.get('K_PERIOD', 14)
    d_period = STOCHASTIC_RSI.get('D_PERIOD', 3)
    smooth_k = STOCHASTIC_RSI.get('SMOOTH_K', 3)

    # 检查参数是否有效
    if k_period <= 0 or d_period <= 0 or smooth_k <= 0:
        raise ValueError("K_PERIOD, D_PERIOD 和 SMOOTH_K 必须大于零。")

    # 计算 RSI
    delta = stock_data['close'].diff()
    gain = np.maximum(delta, 0)  # 向量化计算涨幅
    loss = np.maximum(-delta, 0)  # 向量化计算跌幅
    avg_gain = gain.ewm(span=14, adjust=False).mean()
    avg_loss = loss.ewm(span=14, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-10)  # 避免除零
    rsi = 100 - (100 / (1 + rs))

    # 计算 %K
    lowest_low = stock_data['close'].rolling(window=k_period).min()
    highest_high = stock_data['close'].rolling(window=k_period).max()
    k = ((rsi - lowest_low) / (highest_high - lowest_low)) * 100
    k = pd.to_numeric(k, errors='coerce')  # 确保 %K 是数值类型

    # 平滑 %K
    k_smoothed = k.rolling(window=smooth_k).mean()

    # 计算 %D
    d = k_smoothed.rolling(window=d_period).mean()

    return pd.DataFrame({'%K': k_smoothed, '%D': d}, index=stock_data.index)

def plot_stochastic_rsi(stock_data, stochastic_rsi_data):
    """
    绘制包含股价和 Stochastic RSI 的图表
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    ax1.plot(stock_data.index, stock_data['close'], label='Stock Price', color='blue')
    ax1.set_title('Stock Price')
    ax1.set_ylabel('Price')
    ax1.legend()

    ax2.plot(stochastic_rsi_data.index, stochastic_rsi_data['%K'], label='%K', color='orange')
    ax2.plot(stochastic_rsi_data.index, stochastic_rsi_data['%D'], label='%D', color='green', linestyle='--')
    ax2.axhline(y=80, color='r', linestyle='--', label='Overbought (80)')
    ax2.axhline(y=20, color='g', linestyle='--', label='Oversold (20)')
    ax2.set_title('Stochastic RSI')
    ax2.set_ylabel('Stochastic RSI')
    ax2.legend()

    plt.tight_layout()
    plt.show()

def generate_stochastic_rsi_operation_suggestion(stochastic_rsi_data):
    """
    根据 Stochastic RSI 指标生成详细操作建议

    参数:
    stochastic_rsi_data (pd.DataFrame): 包含 %K 和 %D 的 Stochastic RSI 数据

    返回:
    str: 操作建议
    """
    # 获取最新的 %K 和 %D 值
    latest_k = stochastic_rsi_data['%K'].iloc[-1]
    latest_d = stochastic_rsi_data['%D'].iloc[-1]

    # 设置超买和超卖阈值
    overbought = 80
    oversold = 20

    # 初始化操作建议
    result = '观望'
    if latest_k > overbought and latest_d > overbought:
        suggestion = f"Stochastic RSI - %K: {latest_k:.2f}, %D: {latest_d:.2f}，市场处于超买区，价格可能过高，存在回调风险。\n📌 建议：卖出或减仓。"
        result = "卖出"

    elif latest_k < oversold and latest_d < oversold:
        suggestion = f"Stochastic RSI - %K: {latest_k:.2f}, %D: {latest_d:.2f}，市场处于超卖区，可能存在反弹机会。\n📌 建议：买入或加仓。"
        result = "买入"

    elif latest_k > latest_d and latest_k < overbought:
        suggestion = f"Stochastic RSI - %K: {latest_k:.2f}, %D: {latest_d:.2f}，%K 上穿 %D，显示潜在上涨信号。\n📌 建议：买入信号，准备入场。"
        result =  "买入"

    elif latest_k < latest_d and latest_k > oversold:
        suggestion = f"Stochastic RSI - %K: {latest_k:.2f}, %D: {latest_d:.2f}，%K 下穿 %D，显示潜在下跌信号。\n📌 建议：卖出信号，准备减仓。"
        result  = "卖出"

    else:
        suggestion = f"Stochastic RSI - %K: {latest_k:.2f}, %D: {latest_d:.2f}，目前指标无明显趋势，市场震荡整理。\n📌 建议：观望，等待更明确信号。"
        result =  "观望"

    print(suggestion)
    print("-----------------------------------------------------------------------------------------------------")

    return result
