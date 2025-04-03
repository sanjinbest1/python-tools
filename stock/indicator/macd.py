import pandas as pd
import matplotlib.pyplot as plt
from stock.data.config import MACD_CONFIG  # 从配置文件导入参数


def calculate_macd(data):
    """
    计算MACD指标

    参数:
    data (pd.Series): 股票的收盘价数据

    返回:
    dict: 包含 'macd', 'signal', 'hist' 的字典
    """
    if not isinstance(data, pd.Series):
        raise ValueError("输入的 data 必须是 Pandas Series 类型")

    fast_period = MACD_CONFIG["fast_period"]
    slow_period = MACD_CONFIG["slow_period"]
    signal_period = MACD_CONFIG["signal_period"]

    # 计算快速和慢速EMA
    fast_ema = data.ewm(span=fast_period, adjust=False).mean()
    slow_ema = data.ewm(span=slow_period, adjust=False).mean()

    # 计算MACD
    macd = fast_ema - slow_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    hist = macd - signal

    # 确保返回的是 Pandas Series
    macd = pd.Series(macd, index=data.index)
    signal = pd.Series(signal, index=data.index)
    hist = pd.Series(hist, index=data.index)

    return {'macd': macd, 'signal': signal, 'hist': hist}


def generate_macd_signal(macd, signal, cost=None):
    """
    根据MACD指标生成操作建议

    参数:
    - macd (pd.Series): 计算得到的MACD值
    - signal (pd.Series): 计算得到的信号线值
    - cost (float): 当前持仓的成本价，只有在有持仓时需要提供

    返回:
    - 操作建议字符串
    """

    # **数据完整性检查**
    if not isinstance(macd, pd.Series):
        macd = pd.Series(macd)
    if not isinstance(signal, pd.Series):
        signal = pd.Series(signal)

    # **确保数据至少有两条**
    if len(macd) < 2 or len(signal) < 2:
        print("MACD 或 Signal 数据不足，返回'观望'")
        return "观望"

    # **数据类型转换**
    macd = pd.to_numeric(macd, errors='coerce')
    signal = pd.to_numeric(signal, errors='coerce')

    # **检查是否存在 NaN 值**
    if macd.isna().any() or signal.isna().any():
        print("MACD 或 Signal 存在 NaN 值，请检查数据")
        print("MACD:", macd.tail())
        print("Signal:", signal.tail())
        return "观望"

    # **仓位状态**
    current_position = 'empty' if cost is None else 'long'

    # **计算交叉信号**
    buy_signal = macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]  # 黄金交叉
    sell_signal = macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]  # 死亡交叉

    # **默认建议**
    simple_suggestion = "观望"
    detailed_suggestion = "MACD - {:.2f}, 观望，无明显信号。".format(macd.iloc[-1])

    # **交易逻辑**
    if current_position == 'empty':
        if buy_signal:
            detailed_suggestion = "MACD - {:.2f}, 买入信号，建议在当前价格买入。".format(macd.iloc[-1])
            simple_suggestion = "买入"
    elif current_position == 'long':
        if sell_signal:
            detailed_suggestion = "MACD - {:.2f}, 卖出信号，建议卖出，市场出现死亡交叉。".format(macd.iloc[-1])
            simple_suggestion = "卖出"
        elif macd.iloc[-1] < 0:
            detailed_suggestion = "MACD - {:.2f}, 市场下行信号，考虑止损或卖出。".format(macd.iloc[-1])
            simple_suggestion = "卖出"
        else:
            detailed_suggestion = "MACD - {:.2f}, 持有信号，市场处于上涨趋势中，建议继续持有。".format(macd.iloc[-1])

    print(detailed_suggestion)
    return simple_suggestion


def plot_macd_with_signal(data, macd_dict, cost=None, config=MACD_CONFIG, time_period=None):
    """
    绘制MACD图，并显示操作建议
    参数:
    - data (pd.Series): 股票的收盘价数据
    - macd_dict (dict): 包含 'macd', 'signal', 'hist' 的字典
    - cost (float): 当前持仓的成本价，只有在有持仓时需要提供
    - time_period (int): 绘制的时间段，默认为None表示全部数据
    """

    fast_period = config["fast_period"]
    slow_period = config["slow_period"]
    signal_period = config["signal_period"]

    if time_period:
        # 根据指定的时间段来选择数据
        data = data.tail(time_period)
        macd_dict['macd'] = macd_dict['macd'].tail(time_period)
        macd_dict['signal'] = macd_dict['signal'].tail(time_period)
        macd_dict['hist'] = macd_dict['hist'].tail(time_period)

    # 使用数据的日期索引来绘制X轴
    plt.figure(figsize=(12, 8))

    # 绘制股价图
    plt.subplot(3, 1, 1)
    plt.plot(data.index, data, label='Stock Price', color='blue')  # 使用data的index作为X轴
    plt.title('Stock Price')
    plt.legend()

    # 绘制MACD图
    plt.subplot(3, 1, 2)
    plt.plot(macd_dict['macd'].index, macd_dict['macd'], label=f'MACD ({fast_period},{slow_period},{signal_period})')  # 使用macd的index作为X轴
    plt.plot(macd_dict['signal'].index, macd_dict['signal'], label=f'Signal ({signal_period})', linestyle='--')
    plt.bar(macd_dict['hist'].index, macd_dict['hist'], label='MACD Histogram', alpha=0.3)
    plt.title(f'MACD ({fast_period},{slow_period},{signal_period})')
    plt.legend()

    plt.tight_layout()
    plt.show()

    # 生成操作建议
    signal_advice = generate_macd_signal(macd_dict['macd'], macd_dict['signal'], cost=cost)
    return signal_advice


# **测试代码**
if __name__ == "__main__":
    # 生成示例数据
    dates = pd.date_range(start="2024-01-01", periods=100, freq='D')
    prices = pd.Series([100 + i + (i % 5) * 2 for i in range(100)], index=dates)  # 生成模拟股价数据

    # 计算MACD
    macd_results = calculate_macd(prices)

    # 生成MACD交易信号
    signal = generate_macd_signal(macd_results['macd'], macd_results['signal'])

    # 绘制MACD图
    plot_macd_with_signal(prices, macd_results)
