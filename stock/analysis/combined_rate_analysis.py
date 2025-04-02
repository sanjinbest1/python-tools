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
    '短线': {
        'rsi': {'买入': 0.25, '卖出': 0.25, '观望': 0.1},
        'macd': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'bollinger': {'买入': 0.25, '卖出': 0.25, '观望': 0.1},
        'obv': {'买入': 0.1, '卖出': 0.1, '观望': 0.05},
        'vwap': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'stochastic_rsi': {'买入': 0.2, '卖出': 0.2, '观望': 0.05},
        'adx': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'atr': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'keltner': {'买入': 0.1, '卖出': 0.1, '观望': 0.05}
    },
    '中线': {
        'rsi': {'买入': 0.1, '卖出': 0.1, '观望': 0.1},
        'macd': {'买入': 0.25, '卖出': 0.25, '观望': 0.1},
        'bollinger': {'买入': 0.15, '卖出': 0.15, '观望': 0.1},
        'obv': {'买入': 0.2, '卖出': 0.2, '观望': 0.1},
        'vwap': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'stochastic_rsi': {'买入': 0.05, '卖出': 0.05, '观望': 0.1},
        'adx': {'买入': 0.1, '卖出': 0.1, '观望': 0.05},
        'atr': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'keltner': {'买入': 0.1, '卖出': 0.1, '观望': 0.05}
    },
    '长线': {
        'rsi': {'买入': 0.05, '卖出': 0.05, '观望': 0.1},
        'macd': {'买入': 0.2, '卖出': 0.2, '观望': 0.1},
        'bollinger': {'买入': 0.05, '卖出': 0.05, '观望': 0.1},
        'obv': {'买入': 0.25, '卖出': 0.15, '观望': 0.1},
        'vwap': {'买入': 0.15, '卖出': 0.15, '观望': 0.1},
        'stochastic_rsi': {'买入': 0.05, '卖出': 0.05, '观望': 0.1},
        'adx': {'买入': 0.05, '卖出': 0.05, '观望': 0.1},
        'atr': {'买入': 0.05, '卖出': 0.05, '观望': 0.1},
        'keltner': {'买入': 0.05, '卖出': 0.05, '观望': 0.1}
    },
    '趋势性市场': {
        'rsi': {'买入': 0.1, '卖出': 0.1, '观望': 0.05},
        'macd': {'买入': 0.3, '卖出': 0.3, '观望': 0.1},
        'bollinger': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'obv': {'买入': 0.1, '卖出': 0.1, '观望': 0.05},
        'vwap': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'stochastic_rsi': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'adx': {'买入': 0.2, '卖出': 0.2, '观望': 0.05},
        'atr': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'keltner': {'买入': 0.05, '卖出': 0.05, '观望': 0.05}
    },
    '震荡市场': {
        'rsi': {'买入': 0.25, '卖出': 0.25, '观望': 0.1},
        'macd': {'买入': 0.05, '卖出': 0.05, '观望': 0.1},
        'bollinger': {'买入': 0.25, '卖出': 0.25, '观望': 0.1},
        'obv': {'买入': 0.1, '卖出': 0.1, '观望': 0.05},
        'vwap': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'stochastic_rsi': {'买入': 0.15, '卖出': 0.15, '观望': 0.05},
        'adx': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'atr': {'买入': 0.05, '卖出': 0.05, '观望': 0.05},
        'keltner': {'买入': 0.1, '卖出': 0.1, '观望': 0.05}
    }
}


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

def generate_combined_recommendation(indicator_results, market_type='震荡市场', trading_style='短线'):
    """
    根据指定的市场类型和交易风格生成综合操作建议。
    """
    weights = indicator_weights[trading_style]
    buy_score, sell_score, hold_score = 0, 0, 0

    for indicator, recommendation in indicator_results.items():
        if recommendation in weights[indicator]:
            if recommendation == "买入":
                buy_score += weights[indicator]['买入']
            elif recommendation == "卖出":
                sell_score += weights[indicator]['卖出']
            else:
                hold_score += weights[indicator]['观望']

    if buy_score > sell_score and buy_score > hold_score:
        return "买入"
    elif sell_score > buy_score and sell_score > hold_score:
        return "卖出"
    else:
        return "观望"

def analyze(stock, stock_data, market_type='震荡市场', trading_style='短线'):
    """
    执行完整的分析流程，计算各指标并生成最终操作建议。
    """
    print(f"正在分析股票: {stock.ticker} - {market_type} - {trading_style}")
    indicator_results = calculate_indicators(stock, stock_data)
    combined_recommendation = generate_combined_recommendation(indicator_results, market_type, trading_style)
    print(f"最终综合建议: {combined_recommendation}\n")
    return combined_recommendation

# 示例：分析不同股票
def main():
    stocks = ['sh.600570']
    market_types = ['震荡市场', '趋势性市场']
    trading_styles = ['短线', '中线', '长线']

    for ticker in stocks:
        stock = StockAnalysis(ticker, '2025-01-01', '2025-04-02', initial_cash=100000,
                              rsi_window_list=[6, 24], fast_period=12, slow_period=26, signal_period=9)
        stock_data = stock.data_fetcher.fetch_data()

        for market_type in market_types:
            for trading_style in trading_styles:
                analyze(stock, stock_data, market_type, trading_style)

if __name__ == '__main__':
    main()
