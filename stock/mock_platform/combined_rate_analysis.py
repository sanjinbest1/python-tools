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

def calculate_indicators(stock, stock_data):
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

def calculate_trade_quantity(stock, recommendation, stop_loss_pct, stop_gain_pct, stock_data):
    """
    计算本次建议的买入或卖出量
    :param stock: StockAnalysis 对象，包含当前持仓信息
    :param recommendation: 交易建议（"买入"、"卖出"、"观望"）
    :param stop_loss_pct: 设定的止损百分比
    :param stop_gain_pct: 设定的止盈百分比
    :param stock_data: 最新的股票数据（包括收盘价）
    :return: 建议的交易数量（正数表示买入，负数表示卖出）
    """
    # 如果 last_price 为 None，从 stock_data 中获取最新的价格
    current_price = stock.last_price if stock.last_price is not None else stock_data['close'].iloc[-1]

    if current_price is None:
        raise ValueError("当前股价无效，请检查数据源")

    available_cash = stock.capital  # 可用资金

    # 获取当前持仓，假设你暂时用一个字典表示持仓
    current_position = stock.positions.get(stock.ticker, 0) if hasattr(stock, 'positions') else 0
    avg_cost = 0  # 如果没有持仓成本，暂时设为0

    # 计算最大买入量（基于本金和止损点）
    max_risk_amount = available_cash * 0.02  # 单次交易最大亏损2%本金
    max_buy_quantity = max_risk_amount / (current_price * stop_loss_pct)
    max_buy_quantity = min(max_buy_quantity, available_cash // current_price)  # 资金约束

    # 计算最大卖出量（基于止盈点）
    max_sell_quantity = current_position if avg_cost * (1 + stop_gain_pct) <= current_price else 0

    # 生成最终交易量
    if recommendation == "买入":
        return int(max_buy_quantity)
    elif recommendation == "卖出":
        return -int(max_sell_quantity)
    else:
        return 0  # 观望不交易



def analyze(stock, stock_data, stop_loss_pct=0.05, stop_gain_pct=0.10):
    """
    执行完整的分析流程，计算各指标并生成最终操作建议。
    :param stock: StockAnalysis 对象
    :param stock_data: 股票数据
    :param stop_loss_pct: 设定的止损百分比
    :param stop_gain_pct: 设定的止盈百分比
    """
    print(f"正在分析股票: {stock.ticker}")
    indicator_results = calculate_indicators(stock, stock_data)
    combined_recommendation = generate_combined_recommendation(indicator_results)

    # 计算建议的交易数量
    suggested_quantity = calculate_trade_quantity(stock, combined_recommendation, stop_loss_pct, stop_gain_pct,stock_data)

    print(f"最终综合建议: {combined_recommendation}, 建议交易量: {suggested_quantity} 股\n")
    return combined_recommendation, suggested_quantity

def main():
    stocks = ['sz.300377']
    end_date = '2025-04-03'
    lookback_years = 3
    start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=lookback_years * 365)).strftime("%Y-%m-%d")

    for ticker in stocks:
        stock = StockAnalysis(ticker, start_date, end_date, initial_cash=100000,
                              rsi_window_list=[6, 24], fast_period=12, slow_period=26, signal_period=9)
        stock_data = stock.data_fetcher.fetch_data()

        analyze(stock, stock_data)

if __name__ == '__main__':
    main()
