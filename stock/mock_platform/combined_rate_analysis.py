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
indicator_weights = {'rsi': {'买入': 0.04618915327938157, '卖出': 0.04618915327938157, '观望': 0.023094576639690785}, 'macd': {'买入': 0.04150259693199662, '卖出': 0.04150259693199662, '观望': 0.02075129846599831}, 'bollinger': {'买入': 0.04710713854330233, '卖出': 0.04710713854330233, '观望': 0.023553569271651167}, 'obv': {'买入': 0.041695856987558885, '卖出': 0.041695856987558885, '观望': 0.020847928493779443}, 'vwap': {'买入': 0.040439666626404164, '卖出': 0.040439666626404164, '观望': 0.020219833313202082}, 'stochastic_rsi': {'买入': 0.04184080202923059, '卖出': 0.04184080202923059, '观望': 0.020920401014615293}, 'adx': {'买入': 0.0473003985988646, '卖出': 0.0473003985988646, '观望': 0.0236501992994323}, 'atr': {'买入': 0.0473003985988646, '卖出': 0.0473003985988646, '观望': 0.0236501992994323}, 'keltner': {'买入': 0.04662398840439667, '卖出': 0.04662398840439667, '观望': 0.023311994202198334}}

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
    # stocks = ['sh.600570']
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
