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

#整体指标建议
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
    :param stock: StockAnalysis 对象
    :param stock_data: 股票数据
    :param stop_loss_pct: 设定的止损百分比
    :param stop_gain_pct: 设定的止盈百分比
    """
    print(f"正在分析股票: {stock.ticker}")
    indicator_results = calculate_indicators(stock_data)
    combined_recommendation = generate_combined_recommendation(indicator_results)


    print(f"最终综合建议: {combined_recommendation}")
    return combined_recommendation

def main():
    stocks = ['01810']
    end_date = '2025-04-07'
    lookback_years = 1
    start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=lookback_years * 365)).strftime("%Y-%m-%d")

    for ticker in stocks:
        stock = StockAnalysis(ticker, start_date, end_date)
        stock_data = stock.data_fetcher.fetch_data()

        analyze(stock, stock_data)

if __name__ == '__main__':
    main()
