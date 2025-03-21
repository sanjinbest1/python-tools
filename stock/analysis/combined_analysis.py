from stock.data.stock_analysis import StockAnalysis
from stock.indicator.rsi import *
from stock.indicator.macd import *
from stock.indicator.bollinger_bands import *
import matplotlib.pyplot as plt
from stock.indicator.obv import *
from stock.indicator.vwap import *
from stock.indicator.stochastic_rsi import *
from stock.indicator.adx import *  # 新增导入 ADX 相关函数
from stock.indicator.atr import *  # 新增导入 ATR 相关函数
from stock.indicator.keltner_channel import *


def generate_combined_recommendation(rsi_recommendation, macd_recommendation, bollinger_recommendation, obv_recommendation, vwap_recommendation, stochastic_rsi_recommendation, adx_recommendation, atr_recommendation, keltner_recommendation):
    """
    综合9个指标的推荐，给出统一的操作建议（中文优化版）。
    """
    recommendations = [rsi_recommendation, macd_recommendation, bollinger_recommendation, obv_recommendation, vwap_recommendation, stochastic_rsi_recommendation, adx_recommendation, atr_recommendation, keltner_recommendation]

    # 统计买入和卖出信号的数量
    buy_count = sum(1 for rec in recommendations if "买入" in rec)
    sell_count = sum(1 for rec in recommendations if "卖出" in rec)

    # 所有指标都建议买入
    if buy_count == 9:
        print("强烈买入：所有指标均建议买入，当前可能是绝佳的买点！")
        return "买入"

    # 所有指标都建议卖出
    elif sell_count == 9:
        print("强烈卖出：所有指标均建议卖出，当前可能是离场的好时机！")
        return "卖出"

    # 8个以上指标建议买入
    elif buy_count >= 8:
        print("建议买入：多数指标显示买入信号，机会较大！")
        return "买入"

    # 8个以上指标建议卖出
    elif sell_count >= 8:
        print("建议卖出：多数指标显示卖出信号，应谨慎操作！")
        return "卖出"

    # 信号混杂，建议观望
    else:
        print("观望：指标信号不一致，暂时没有明确的买卖机会。")
        return "观望"


def analyze(stock):
    """
    执行完整的分析流程：获取数据、计算各指标、绘制图表并生成建议
    """
    print(f"正在分析股票: {stock.ticker}")

    # 计算 RSI
    rsi_dict = calculate_rsi_for_multiple_windows(stock.stock_data, stock.rsi_window_list)
    rsi_recommendation = generate_operation_suggestion(rsi_dict, stock.rsi_window_list)
    print(f"RSI 操作建议: {rsi_recommendation}")
    print("-------------------------------------------------------")
    # plot_multiple_rsi(stock.stock_data, rsi_dict, stock.rsi_window_list)

    # 计算 MACD
    macd_dict = calculate_macd(stock.stock_data['close'],
                               fast_period=stock.fast_period,
                               slow_period=stock.slow_period,
                               signal_period=stock.signal_period)
    macd_recommendation = generate_macd_signal(macd_dict['macd'], macd_dict['signal'], cost=stock.cost)
    print(f"MACD 操作建议: {macd_recommendation}")
    print("-------------------------------------------------------")
    # plot_macd_with_signal(stock.stock_data['close'], macd_dict,
    #                       fast_period=stock.fast_period,
    #                       slow_period=stock.slow_period,
    #                       signal_period=stock.signal_period)

    # 计算布林带
    bollinger_data = calculate_bollinger_bands(stock.stock_data,
                                               stock.bollinger_hands_window,
                                               stock.bollinger_hands_num_std)
    bollinger_data = generate_bollinger_signals(bollinger_data)
    bollinger_recommendation = generate_bollinger_operations(bollinger_data)
    print(f"布林带操作建议: {bollinger_recommendation}")
    print("-------------------------------------------------------")
    # plot_bollinger_bands(bollinger_data)

    # 计算 OBV
    obv_data = calculate_obv(stock.stock_data)
    obv_recommendation = generate_obv_operation_suggestion(obv_data, stock.stock_data)
    print(f"OBV 操作建议: {obv_recommendation}")
    print("-------------------------------------------------------")
    # plot_obv(stock.stock_data, obv_data)

    # 计算 VWAP
    vwap_data = calculate_vwap(stock.stock_data)
    vwap_recommendation = generate_vwap_operation_suggestion(stock.stock_data, vwap_data)
    print(f"VWAP 操作建议: {vwap_recommendation}")
    print("-------------------------------------------------------")
    # plot_vwap(stock.stock_data, vwap_data)

    # 计算 Stochastic RSI
    stochastic_rsi_data = calculate_stochastic_rsi(stock.stock_data)
    stochastic_rsi_recommendation = generate_stochastic_rsi_operation_suggestion(stochastic_rsi_data)
    print(f"Stochastic RSI 操作建议: {stochastic_rsi_recommendation}")
    print("-------------------------------------------------------")
    # plot_stochastic_rsi(stock.stock_data, stochastic_rsi_data)

    # 计算 ADX
    adx_data = calculate_adx(stock.stock_data)
    adx_recommendation = generate_adx_operation_suggestion(adx_data)
    print(f"ADX 操作建议: {adx_recommendation}")
    print("-------------------------------------------------------")

    # 计算 ATR
    atr_data = calculate_atr(stock.stock_data)
    atr_recommendation = generate_atr_operation_suggestion(atr_data)
    print(f"ATR 操作建议: {atr_recommendation}")
    print("-------------------------------------------------------")

    # 计算 Keltner Channel
    keltner_data = calculate_keltner_channel(stock.stock_data)
    keltner_recommendation = generate_keltner_channel_operation_suggestion(keltner_data, stock.stock_data)
    print(f"Keltner Channel 操作建议: {keltner_recommendation}")
    print("-------------------------------------------------------")
    # plot_keltner_channel(stock.stock_data, keltner_data)

    # 综合九个指标的建议
    combined_recommendation = generate_combined_recommendation(rsi_recommendation, macd_recommendation, bollinger_recommendation, obv_recommendation, vwap_recommendation, stochastic_rsi_recommendation, adx_recommendation, atr_recommendation, keltner_recommendation)
    print(f"最终综合建议: {combined_recommendation}")


# 示例：创建 StockAnalysis 对象并执行分析
if __name__ == '__main__':
    ticker ='sh.600570'  # 股票代码
    start_date = '2024-10-01'
    end_date = '2025-03-10'
    window_list = [6, 24]  # RSI的多个窗口

    stock = StockAnalysis(ticker, start_date, end_date,
                          rsi_window_list=window_list,
                          fast_period=12, slow_period=26, signal_period=9)
    analyze(stock)

    # 600446、601939、002657、300377
