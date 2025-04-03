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
    k_period = STOCHASTIC_RSI['K_PERIOD']
    d_period = STOCHASTIC_RSI['D_PERIOD']
    smooth_k = STOCHASTIC_RSI['SMOOTH_K']

    # 计算 RSI
    delta = stock_data['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(span=14, adjust=False).mean()
    avg_loss = loss.ewm(span=14, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi = np.where(avg_loss == 0, 100, rsi)

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
    根据 Stochastic RSI 指标生成操作建议

    参数:
    stochastic_rsi_data (pd.DataFrame): 包含 %K 和 %D 的 Stochastic RSI 数据

    返回:
    str: 操作建议
    """
    latest_k = stochastic_rsi_data['%K'].iloc[-1]
    latest_d = stochastic_rsi_data['%D'].iloc[-1]
    overbought = 80
    oversold = 20

    simple_suggestion = "观望"
    if latest_k > overbought and latest_d > overbought:
        detailed_suggestion = "Stochastic RSI - %K: {:.2f}, %D: {:.2f}，超买，建议卖出或减仓。".format(latest_k, latest_d)
        simple_suggestion = "卖出"
    elif latest_k < oversold and latest_d < oversold:
        detailed_suggestion = "Stochastic RSI - %K: {:.2f}, %D: {:.2f}，超卖，建议买入或加仓。".format(latest_k, latest_d)
        simple_suggestion = "买入"
    elif latest_k > latest_d and latest_k < overbought:
        detailed_suggestion = "Stochastic RSI - %K: {:.2f}, %D: {:.2f}，%K 上穿 %D 且未超买，可能是买入信号，建议关注。".format(latest_k, latest_d)
        simple_suggestion = "买入"
    elif latest_k < latest_d and latest_k > oversold:
        detailed_suggestion = "Stochastic RSI - %K: {:.2f}, %D: {:.2f}，%K 下穿 %D 且未超卖，可能是卖出信号，建议关注。".format(latest_k, latest_d)
        simple_suggestion = "卖出"
    else:
        detailed_suggestion = "Stochastic RSI - %K: {:.2f}, %D: {:.2f}，指标无明显趋势，建议观望。".format(latest_k, latest_d)

    print(detailed_suggestion)
    return simple_suggestion


