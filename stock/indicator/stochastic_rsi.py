import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def calculate_stochastic_rsi(stock_data, k_period=21, d_period=5, smooth_k=5):
    """
    计算随机 RSI（Stochastic RSI）指标

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价
    k_period (int): %K 周期，默认为 14
    d_period (int): %D 周期，默认为 3
    smooth_k (int): 平滑 %K 的周期，默认为 3

    返回:
    pd.DataFrame: 包含 %K 和 %D 的 DataFrame
    """
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

    stochastic_rsi_df = pd.DataFrame({
        '%K': k_smoothed,
        '%D': d
    }, index=stock_data.index)
    return stochastic_rsi_df


def plot_stochastic_rsi(stock_data, stochastic_rsi_data):
    """
    绘制包含股价和 Stochastic RSI 的图表

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价
    stochastic_rsi_data (pd.DataFrame): 包含 %K 和 %D 的 Stochastic RSI 数据
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # 绘制股票收盘价图
    ax1.plot(stock_data.index, stock_data['close'], label='Stock Price', color='blue')
    ax1.set_title('Stock Price', fontsize=14)
    ax1.set_ylabel('Stock Price', color='blue')
    ax1.legend(loc='upper left')

    # 绘制 Stochastic RSI 图
    ax2.plot(stochastic_rsi_data.index, stochastic_rsi_data['%K'], label='%K', color='orange')
    ax2.plot(stochastic_rsi_data.index, stochastic_rsi_data['%D'], label='%D', color='green', linestyle='--')
    ax2.axhline(y=80, color='r', linestyle='--', label='Overbought (80)')
    ax2.axhline(y=20, color='g', linestyle='--', label='Oversold (20)')
    ax2.set_title('Stochastic RSI', fontsize=14)
    ax2.set_ylabel('Stochastic RSI', color='orange')
    ax2.legend(loc='upper left')

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


