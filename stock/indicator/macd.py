import matplotlib.pyplot as plt

def calculate_macd(data, fast_period=5, slow_period=13, signal_period=5):
    """
    计算MACD指标

    参数:
    data (pd.Series): 股票的收盘价数据
    fast_period (int): 快速EMA的时间窗口
    slow_period (int): 慢速EMA的时间窗口
    signal_period (int): 信号线的时间窗口

    返回:
    dict: 包含' macd', 'signal', 'hist'的字典
    """
    # 计算快速和慢速EMA
    fast_ema = data.ewm(span=fast_period, adjust=False).mean()
    slow_ema = data.ewm(span=slow_period, adjust=False).mean()

    # 计算MACD
    macd = fast_ema - slow_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    hist = macd - signal

    return {'macd': macd, 'signal': signal, 'hist': hist}

def generate_macd_signal(macd, signal, cost=None):
    """
    根据MACD指标生成操作建议

    参数:
    - macd (pd.Series): 计算得到的MACD值
    - signal (pd.Series): 计算得到的信号线值
    - current_position (str): 当前持仓状态，'long'代表有仓位，'empty'代表空仓。默认为None
    - cost (float): 当前持仓的成本价，只有在有持仓时需要提供

    返回:
    - 操作建议字符串
    """
    current_position = 'empty'
    if cost is not None:
        current_position = 'long'

    # 判断是否有交叉信号
    buy_signal = macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]  # 黄金交叉
    sell_signal = macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]  # 死亡交叉

    # 如果当前没有仓位
    if current_position == 'empty':
        if buy_signal:
            return "买入信号：建议在当前价格买入。"
        else:
            return "暂无买入信号，请保持观望。"

    # 如果当前有仓位
    elif current_position == 'long':
        # 如果持仓成本存在，判断是否卖出
        if cost is not None:
            if sell_signal:
                return f"卖出信号：建议卖出，当前持仓成本为 {cost}，市场出现死亡交叉。"
            elif macd.iloc[-1] < 0:
                return f"市场下行信号：当前持仓成本为 {cost}，考虑止损或卖出。"
            else:
                return f"持有信号：市场处于上涨趋势中，建议继续持有。"
        else:
            return "有仓位，但未提供成本，建议关注市场信号，谨慎操作。"

    return "无有效持仓信号或操作建议。"

def plot_macd_with_signal(data, macd_dict, cost=None, fast_period=5, slow_period=13, signal_period=5, time_period=None):
    """
    绘制MACD图，并显示操作建议
    参数:
    - data (pd.Series): 股票的收盘价数据
    - macd_dict (dict): 包含 'macd', 'signal', 'hist' 的字典
    - current_position (str): 当前持仓状态，'long'代表有仓位，'empty'代表空仓。默认为None
    - cost (float): 当前持仓的成本价，只有在有持仓时需要提供
    - time_period (int): 绘制的时间段，默认为None表示全部数据
    """

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
    print(signal_advice)
