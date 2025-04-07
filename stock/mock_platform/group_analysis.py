import datetime
from datetime import timedelta
from stock.data.stock_analysis import StockAnalysis
from stock.indicator.rsi import *
from stock.indicator.macd import *
from stock.indicator.bollinger_bands import *
from stock.indicator.obv import *
from stock.indicator.vwap import *
from stock.indicator.stochastic_rsi import *
from stock.indicator.adx import *
from stock.indicator.atr import *
from stock.indicator.keltner_channel import *

# 设定指标权重
indicator_weights = {
    'rsi': {'买入': 0.0456, '卖出': 0.0456, '观望': 0.0228},
    'macd': {'买入': 0.0427, '卖出': 0.0427, '观望': 0.0213},
    'bollinger': {'买入': 0.0468, '卖出': 0.0468, '观望': 0.0234},
    'obv': {'买入': 0.0427, '卖出': 0.0427, '观望': 0.0213},
    'vwap': {'买入': 0.0422, '卖出': 0.0422, '观望': 0.0211},
    'stochastic_rsi': {'买入': 0.0381, '卖出': 0.0381, '观望': 0.0191},
    'adx': {'买入': 0.0476, '卖出': 0.0476, '观望': 0.0238},
    'atr': {'买入': 0.0476, '卖出': 0.0476, '观望': 0.0238},
    'keltner': {'买入': 0.0467, '卖出': 0.0467, '观望': 0.0233}
}

def calculate_indicators(stock_data):
    """
    计算所有技术指标并返回建议
    """
    indicators = {
        'rsi': generate_operation_suggestion(
            calculate_rsi_for_multiple_windows(stock_data)),
        'macd': generate_macd_signal(
            *calculate_macd(stock_data['close'])),
        'bollinger': generate_bollinger_operations(
            generate_bollinger_signals(
                calculate_bollinger_bands(stock_data)
            )
        ),
        'obv': generate_obv_operation_suggestion(calculate_obv(stock_data), stock_data),
        'vwap': generate_vwap_operation_suggestion(stock_data, calculate_vwap(stock_data)),
        'stochastic_rsi': generate_stochastic_rsi_operation_suggestion(calculate_stochastic_rsi(stock_data)),
        'adx': generate_adx_operation_suggestion(calculate_adx_safe(stock_data)),
        'atr': generate_atr_operation_suggestion(calculate_atr(stock_data)),
        'keltner': generate_keltner_channel_operation_suggestion(
            calculate_keltner_channel(stock_data))
    }
    return indicators

def strategy_1(stock_data):
    """
    策略 1 - 趋势确认与逆势反弹组合 (RSI, ADX, Stochastic RSI)
    """
    indicators = calculate_indicators(stock_data)
    rsi_suggestion = indicators['rsi']
    adx_suggestion = indicators['adx']
    stochastic_rsi_suggestion = indicators['stochastic_rsi']

    # 若RSI显示超卖，且ADX较强（大于25），Stochastic RSI也在超卖区域，则买入
    if rsi_suggestion == "买入" and adx_suggestion == "买入" and stochastic_rsi_suggestion == "买入":
        return "买入"
    elif rsi_suggestion == "卖出" or adx_suggestion == "卖出":
        return "卖出"
    else:
        return "观望"

def strategy_2(stock_data):
    """
    策略 2 - 反弹确认与波动性保护组合 (布林带, Keltner Channel, ATR)
    """
    indicators = calculate_indicators(stock_data)
    bollinger_suggestion = indicators['bollinger']
    keltner_suggestion = indicators['keltner']
    atr_suggestion = indicators['atr']

    # 若布林带和Keltner信号同时显示超卖，并且ATR波动较大，考虑反弹买入
    if bollinger_suggestion == "买入" and keltner_suggestion == "买入" and atr_suggestion != "卖出":
        return "买入"
    else:
        return "观望"

def strategy_3(stock_data):
    """
    策略 3 - 动量与流动性组合 (VWAP, OBV, MACD)
    """
    indicators = calculate_indicators(stock_data)
    vwap_suggestion = indicators['vwap']
    obv_suggestion = indicators['obv']
    macd_suggestion = indicators['macd']

    # 若VWAP和OBV显示多头，且MACD显示买入信号，则买入
    if vwap_suggestion == "买入" and obv_suggestion == "买入" and macd_suggestion == "买入":
        return "买入"
    else:
        return "观望"

def strategy_4(stock_data):
    """
    策略 4 - 风险控制组合 (RSI, ADX, ATR)
    """
    indicators = calculate_indicators(stock_data)
    rsi_suggestion = indicators['rsi']
    adx_suggestion = indicators['adx']
    atr_suggestion = indicators['atr']

    # 若RSI超买/超卖，ADX强趋势时，结合ATR波动性调整止损
    if rsi_suggestion == "卖出" and adx_suggestion == "买入" and atr_suggestion != "卖出":
        return "卖出"  # 提醒卖出并设置止损
    else:
        return "观望"

def final_advice(stock_data):
    """
    综合不同策略的建议，输出最终操作建议
    """
    strategy_1_advice = strategy_1(stock_data)
    strategy_2_advice = strategy_2(stock_data)
    strategy_3_advice = strategy_3(stock_data)
    strategy_4_advice = strategy_4(stock_data)

    # 输出每种策略的建议
    print("策略 1 (趋势确认与逆势反弹):", strategy_1_advice)
    print("策略 2 (反弹确认与波动性保护):", strategy_2_advice)
    print("策略 3 (动量与流动性):", strategy_3_advice)
    print("策略 4 (风险控制):", strategy_4_advice)

    # 综合最终建议，若多个策略都建议买入或卖出，最终建议趋向于此
    combined_suggestion = "观望"
    if strategy_1_advice == "买入" and strategy_2_advice == "买入" and strategy_3_advice == "买入":
        combined_suggestion = "买入"
    elif strategy_1_advice == "卖出" or strategy_2_advice == "卖出" or strategy_3_advice == "卖出":
        combined_suggestion = "卖出"

    return combined_suggestion

def analyze(stock, stock_data):
    """
    执行完整的分析流程，计算各指标并生成最终操作建议。
    :param stock: StockAnalysis 对象
    :param stock_data: 股票数据
    :return: 综合操作建议
    """
    print(f"正在分析股票: {stock.ticker}")
    final_decision = final_advice(stock_data)
    print("最终操作建议:", final_decision)
    return final_decision


def main():
    stocks = ['01810']
    end_date = '2025-04-08'
    lookback_years = 1
    start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=lookback_years * 365)).strftime("%Y-%m-%d")

    for ticker in stocks:
        stock = StockAnalysis(ticker, start_date, end_date)
        stock_data = stock.data_fetcher.fetch_data()

        analyze(stock, stock_data)

if __name__ == '__main__':
    main()
