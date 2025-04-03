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
import datetime
from datetime import timedelta

# 设定指标权重
indicator_weights = {'rsi': {'买入': 0.04556432884347422, '卖出': 0.04556432884347422, '观望': 0.02278216442173711}, 'macd': {'买入': 0.04273107292150488, '卖出': 0.04273107292150488, '观望': 0.02136553646075244}, 'bollinger': {'买入': 0.046771946121690666, '卖出': 0.046771946121690666, '观望': 0.023385973060845333}, 'obv': {'买入': 0.04273107292150488, '卖出': 0.04273107292150488, '观望': 0.02136553646075244}, 'vwap': {'买入': 0.0421737111007896, '卖出': 0.0421737111007896, '观望': 0.0210868555503948}, 'stochastic_rsi': {'买入': 0.038132837900603817, '卖出': 0.038132837900603817, '观望': 0.019066418950301908}, 'adx': {'买入': 0.047607988852763586, '卖出': 0.047607988852763586, '观望': 0.023803994426381793}, 'atr': {'买入': 0.047607988852763586, '卖出': 0.047607988852763586, '观望': 0.023803994426381793}, 'keltner': {'买入': 0.04667905248490478, '卖出': 0.04667905248490478, '观望': 0.02333952624245239}}


def calculate_indicators(stock, stock_data):
    """
    计算所有技术指标并返回建议
    """
    indicators = {
        'rsi': generate_operation_suggestion(
            calculate_rsi_for_multiple_windows(stock_data, stock.rsi_window_list),
            stock.rsi_window_list
        ),
        'macd': generate_macd_signal(
            *calculate_macd(stock_data['close'], stock.fast_period, stock.slow_period, stock.signal_period).values()
        ),
        'bollinger': generate_bollinger_operations(
            generate_bollinger_signals(
                calculate_bollinger_bands(stock_data, stock.bollinger_hands_window, stock.bollinger_hands_num_std)
            )
        ),
        'obv': generate_obv_operation_suggestion(calculate_obv(stock_data), stock_data),
        'vwap': generate_vwap_operation_suggestion(stock_data, calculate_vwap(stock_data)),
        'stochastic_rsi': generate_stochastic_rsi_operation_suggestion(calculate_stochastic_rsi(stock_data)),
        'adx': generate_adx_operation_suggestion(calculate_adx(stock_data)),
        'atr': generate_atr_operation_suggestion(calculate_atr(stock_data)),
        'keltner': generate_keltner_channel_operation_suggestion(
            calculate_keltner_channel(stock_data), stock_data
        )
    }
    return indicators

def generate_combined_recommendation(indicator_results):
    """
    根据指标结果生成综合操作建议。
    """
    buy_score, sell_score, hold_score = 0, 0, 0

    for indicator, recommendation in indicator_results.items():
        if recommendation == "买入":
            buy_score += indicator_weights[indicator]['买入']
        elif recommendation == "卖出":
            sell_score += indicator_weights[indicator]['卖出']
        else:
            hold_score += indicator_weights[indicator]['观望']

    if buy_score > sell_score and buy_score > hold_score:
        return "买入"
    elif sell_score > buy_score and sell_score > hold_score:
        return "卖出"
    else:
        return "观望"

def analyze(stock, stock_data):
    """
    执行完整的分析流程，计算各指标并生成最终操作建议。
    """
    print(f"正在分析股票: {stock.ticker}")
    indicator_results = calculate_indicators(stock, stock_data)
    combined_recommendation = generate_combined_recommendation(indicator_results)
    print(f"最终综合建议: {combined_recommendation}\n")
    return combined_recommendation

# 示例：分析不同股票
def main():
    stocks = ['sz.300377']
    end_date = '2025-04-03'
    lookback_years = 3  # 或者3年
    start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=lookback_years * 365)).strftime("%Y-%m-%d")

    for ticker in stocks:
        # 设定回溯时间跨度（中线：2~3年）

        # 传入 stock_analysis
        stock = StockAnalysis(ticker, start_date, end_date, initial_cash=100000,
                          rsi_window_list=[6, 24], fast_period=12, slow_period=26, signal_period=9)
        stock_data = stock.data_fetcher.fetch_data()

        analyze(stock, stock_data)

if __name__ == '__main__':
    main()
