from stock.data.stock_analysis import StockAnalysis
from stock.indicator.rsi import *
from stock.indicator.macd import *
from stock.indicator.bollinger_bands import *
import matplotlib.pyplot as plt
from stock.indicator.obv import *
from stock.indicator.vwap import *
from stock.indicator.stochastic_rsi import *
from stock.indicator.adx import *
from stock.indicator.atr import *
from stock.indicator.keltner_channel import *

# 设定指标权重
indicator_weights = {
    'rsi': {
        '买入': 0.1,
        '卖出': 0.1,
        '观望': 0.05
    },
    'macd': {
        '买入': 0.15,
        '卖出': 0.15,
        '观望': 0.075
    },
    'bollinger': {
        '买入': 0.1,
        '卖出': 0.1,
        '观望': 0.05
    },
    'obv': {
        '买入': 0.1,
        '卖出': 0.1,
        '观望': 0.05
    },
    'vwap': {
        '买入': 0.1,
        '卖出': 0.1,
        '观望': 0.05
    },
    'stochastic_rsi': {
        '买入': 0.1,
        '卖出': 0.1,
        '观望': 0.05
    },
    'adx': {
        '买入': 0.15,
        '卖出': 0.15,
        '观望': 0.075
    },
    'atr': {
        '买入': 0.1,
        '卖出': 0.1,
        '观望': 0.05
    },
    'keltner': {
        '买入': 0.1,
        '卖出': 0.1,
        '观望': 0.05
    }
}

def generate_combined_recommendation(rsi_result, macd_result, bollinger_result, obv_result, vwap_result,
                                     stochastic_rsi_result, adx_result, atr_result, keltner_result):
    """
    通过指标结果和权重进行综合分析，给出统一的操作建议（中文优化版）。
    """
    buy_score = 0
    sell_score = 0
    hold_score = 0

    result_dict = {
        'rsi': rsi_result,
        'macd': macd_result,
        'bollinger': bollinger_result,
        'obv': obv_result,
        'vwap': vwap_result,
        'stochastic_rsi': stochastic_rsi_result,
        'adx': adx_result,
        'atr': atr_result,
        'keltner': keltner_result
    }

    for indicator, result in result_dict.items():
        if result == "买入":
            buy_score += indicator_weights[indicator]['买入']
        elif result == "卖出":
            sell_score += indicator_weights[indicator]['卖出']
        elif result == "观望":
            hold_score += indicator_weights[indicator]['观望']

    print("买入/卖出/观望", buy_score, sell_score, hold_score)

    if buy_score > sell_score and buy_score > hold_score:
        return "买入"
    elif sell_score > buy_score and sell_score > hold_score:
        return "卖出"
    else:
        return "观望"

def analyze(stock,stock_data):
    """
    执行完整的分析流程：获取数据、计算各指标、绘制图表并生成建议
    """
    print(f"正在分析股票: {stock.ticker}")

    # 计算 RSI
    rsi_dict = calculate_rsi_for_multiple_windows(stock_data, stock.rsi_window_list)
    rsi_recommendation = generate_operation_suggestion(rsi_dict, stock.rsi_window_list)
    print(f"RSI 操作建议: {rsi_recommendation}")
    print("-------------------------------------------------------")
    # plot_multiple_rsi(stock_data, rsi_dict, stock.rsi_window_list)

    # 计算 MACD
    macd_dict = calculate_macd(stock_data['close'],
                               fast_period=stock.fast_period,
                               slow_period=stock.slow_period,
                               signal_period=stock.signal_period)
    macd_recommendation = generate_macd_signal(macd_dict['macd'], macd_dict['signal'], cost=stock.cost)
    print(f"MACD 操作建议: {macd_recommendation}")
    print("-------------------------------------------------------")
    # plot_macd_with_signal(stock_data['close'], macd_dict,
    #                       fast_period=stock.fast_period,
    #                       slow_period=stock.slow_period,
    #                       signal_period=stock.signal_period)

    # 计算布林带
    bollinger_data = calculate_bollinger_bands(stock_data,
                                               stock.bollinger_hands_window,
                                               stock.bollinger_hands_num_std)
    bollinger_data = generate_bollinger_signals(bollinger_data)
    bollinger_recommendation = generate_bollinger_operations(bollinger_data)
    print(f"布林带操作建议: {bollinger_recommendation}")
    print("-------------------------------------------------------")
    # plot_bollinger_bands(bollinger_data)

    # 计算 OBV
    obv_data = calculate_obv(stock_data)
    obv_recommendation = generate_obv_operation_suggestion(obv_data, stock_data)
    print(f"OBV 操作建议: {obv_recommendation}")
    print("-------------------------------------------------------")
    # plot_obv(stock_data, obv_data)

    # 计算 VWAP
    vwap_data = calculate_vwap(stock_data)
    vwap_recommendation = generate_vwap_operation_suggestion(stock_data, vwap_data)
    print(f"VWAP 操作建议: {vwap_recommendation}")
    print("-------------------------------------------------------")
    # plot_vwap(stock_data, vwap_data)

    # 计算 Stochastic RSI
    stochastic_rsi_data = calculate_stochastic_rsi(stock_data)
    stochastic_rsi_recommendation = generate_stochastic_rsi_operation_suggestion(stochastic_rsi_data)
    print(f"Stochastic RSI 操作建议: {stochastic_rsi_recommendation}")
    print("-------------------------------------------------------")
    # plot_stochastic_rsi(stock_data, stochastic_rsi_data)

    # 计算 ADX
    adx_data = calculate_adx(stock_data)
    adx_recommendation = generate_adx_operation_suggestion(adx_data)
    print(f"ADX 操作建议: {adx_recommendation}")
    print("-------------------------------------------------------")

    # 计算 ATR
    atr_data = calculate_atr(stock_data)
    atr_recommendation = generate_atr_operation_suggestion(atr_data)
    print(f"ATR 操作建议: {atr_recommendation}")
    print("-------------------------------------------------------")

    # 计算 Keltner Channel
    keltner_data = calculate_keltner_channel(stock_data)
    keltner_recommendation = generate_keltner_channel_operation_suggestion(keltner_data, stock_data)
    print(f"Keltner Channel 操作建议: {keltner_recommendation}")
    print("-------------------------------------------------------")
    # plot_keltner_channel(stock_data, keltner_data)

    # 综合九个指标的建议
    combined_recommendation = generate_combined_recommendation(rsi_recommendation, macd_recommendation,
                                                               bollinger_recommendation, obv_recommendation,
                                                               vwap_recommendation, stochastic_rsi_recommendation,
                                                               adx_recommendation, atr_recommendation,
                                                               keltner_recommendation)
    print(f"最终综合建议: {combined_recommendation}")
    print("=========================================================")
    print("=========================================================")
    print("=========================================================")
    return combined_recommendation


# 示例：创建 StockAnalysis 对象并执行分析
if __name__ == '__main__':
    ticker ='sh.600570'  # 股票代码
    start_date = '2024-09-23'
    end_date = '2025-03-21'
    window_list = [6, 24]  # RSI的多个窗口

    stock = StockAnalysis(ticker, start_date, end_date,
                          rsi_window_list=window_list,
                          fast_period=12, slow_period=26, signal_period=9)
    stock_data = stock.data_fetcher.fetch_data_from_baostock()
    analyze(stock,stock_data)

    # 600446、601939、002657、300377
