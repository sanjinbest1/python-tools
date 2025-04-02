import pandas as pd
import matplotlib.pyplot as plt


def calculate_keltner_channel(stock_data, period=20, multiplier=2):
    """
    计算 Keltner Channel（KC 通道）

    参数:
    stock_data (pd.DataFrame): 股票数据，包含最高价、最低价、收盘价
    period (int): 计算周期，默认为 20
    multiplier (float): 乘数，默认为 2

    返回:
    pd.DataFrame: 包含中轨、上轨、下轨的 DataFrame
    """
    typical_price = (stock_data['high'] + stock_data['low'] + stock_data['close']) / 3
    ema = typical_price.ewm(span=period, adjust=False).mean()
    atr = (stock_data['high'] - stock_data['low']).abs().rolling(window=period).mean()

    upper_band = ema + multiplier * atr
    lower_band = ema - multiplier * atr

    keltner_df = pd.DataFrame({
        'Middle_Band': ema,
        'Upper_Band': upper_band,
        'Lower_Band': lower_band
    }, index=stock_data.index)
    return keltner_df


def plot_keltner_channel(stock_data, keltner_data):
    """
    绘制 Keltner Channel 图表

    参数:
    stock_data (pd.DataFrame): 股票数据，包含收盘价
    keltner_data (pd.DataFrame): 包含中轨、上轨、下轨的 Keltner Channel 数据
    """
    plt.figure(figsize=(12, 8))

    # 绘制股票收盘价图
    plt.plot(stock_data.index, stock_data['close'], label='Stock Price', color='blue', alpha=0.6, linewidth=1)

    # 绘制 Keltner Channel 中轨
    plt.plot(keltner_data.index, keltner_data['Middle_Band'], label='Middle Band', color='orange', linestyle='-', alpha=0.7, linewidth=1)

    # 绘制 Keltner Channel 上轨
    plt.plot(keltner_data.index, keltner_data['Upper_Band'], label='Upper Band', color='red', linestyle='--', alpha=0.6, linewidth=1)

    # 绘制 Keltner Channel 下轨
    plt.plot(keltner_data.index, keltner_data['Lower_Band'], label='Lower Band', color='green', linestyle='--', alpha=0.6, linewidth=1)

    plt.title('Keltner Channel', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(loc='best', fontsize=12)
    plt.tight_layout()
    plt.show()

def generate_keltner_channel_operation_suggestion(keltner_data, stock_data):
    """
    根据 Keltner Channel 指标生成操作建议

    参数:
    keltner_data (pd.DataFrame): 包含中轨、上轨、下轨的 Keltner Channel 数据
    stock_data (pd.DataFrame): 股票数据，包含收盘价

    返回:
    str: 操作建议
    """
    latest_price = stock_data['close'].iloc[-1]
    latest_upper_band = keltner_data['Upper_Band'].iloc[-1]
    latest_lower_band = keltner_data['Lower_Band'].iloc[-1]

    if latest_price > latest_upper_band:
        detailed_suggestion = "收盘价 - {:.2f}, Keltner 上轨 - {:.2f}, Keltner 下轨 - {:.2f}, 卖出：股价高于 Keltner Channel 上轨，可能存在超买，建议考虑卖出或减仓。".format(latest_price, latest_upper_band, latest_lower_band)
        simple_suggestion = "卖出"
    elif latest_price < latest_lower_band:
        detailed_suggestion = "收盘价 - {:.2f}, Keltner 上轨 - {:.2f}, Keltner 下轨 - {:.2f}, 买入：股价低于 Keltner Channel 下轨，可能存在超卖，建议考虑买入或加仓。".format(latest_price, latest_upper_band, latest_lower_band)
        simple_suggestion = "买入"
    else:
        detailed_suggestion = "收盘价 - {:.2f}, Keltner 上轨 - {:.2f}, Keltner 下轨 - {:.2f}, 观望：股价在 Keltner Channel 区间内，建议观望或根据其他指标综合判断。".format(latest_price, latest_upper_band, latest_lower_band)
        simple_suggestion = "观望"

    print(detailed_suggestion)
    return simple_suggestion
