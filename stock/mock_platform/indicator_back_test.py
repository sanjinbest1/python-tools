import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
from sklearn.metrics import accuracy_score

from stock.data.stock_analysis import StockAnalysis
from stock.mock_platform.combined_rate_analysis import calculate_indicators  # 你提供的计算指标方法

# 设置 matplotlib 支持中文
plt.rcParams['font.sans-serif'] = ['Heiti TC']
plt.rcParams['axes.unicode_minus'] = False


def calculate_future_return(stock_data, trade_date, future_days=[3, 5, 10]):
    """
    计算未来 N 天的收益率
    :param stock_data: 股票数据 DataFrame
    :param trade_date: 当前交易日
    :param future_days: 计算未来收益率的天数列表
    :return: dict, 包含不同天数的收益率
    """
    future_returns = {}
    price = stock_data.loc[trade_date, 'close'] if trade_date in stock_data.index else None

    for days in future_days:
        future_idx = stock_data.index.get_indexer([trade_date + timedelta(days=days)], method='bfill')[0]
        if future_idx >= 0 and future_idx < len(stock_data):
            future_date = stock_data.index[future_idx]
            future_price = stock_data.loc[future_date, 'close']
            if price:
                future_returns[days] = (future_price - price) / price
            else:
                future_returns[days] = None
        else:
            future_returns[days] = None

    return future_returns


def backtest(stock):
    """
    进行回测并评估各个技术指标的准确性
    :param stock: 股票分析实例
    :return: accuracy_data 各指标的准确性数据
    """
    stock_data = stock.data_fetcher.fetch_data()

    # 计算市场波动率（用于市场环境识别）
    stock_data['volatility'] = stock_data['close'].pct_change().rolling(window=20).std()

    # 获取回测时间段内的交易日（默认回测3年）
    trade_dates = stock_data[datetime.strptime(stock.start_date, '%Y-%m-%d'):].index

    # 存储各个指标的预测结果
    accuracy_data = {}

    for trade_date in trade_dates:
        print(f"正在处理日期：{trade_date}")
        # 计算交易日前1年的日期（确保回测数据更长）
        one_year_ago_date = (trade_date - timedelta(days=365)).strftime('%Y-%m-%d')
        # 获取交易日前一年的数据
        data_for_calculation = stock_data[one_year_ago_date: trade_date.strftime('%Y-%m-%d')].copy()

        if len(data_for_calculation) > 50:  # 确保有足够数据计算
            indicator_signals = calculate_indicators(stock, data_for_calculation)  # 获取各个指标的建议
        else:
            continue  # 数据不足，跳过该交易日

        # 确保 accuracy_data 里有所有指标
        for indicator in indicator_signals.keys():
            if indicator not in accuracy_data:
                accuracy_data[indicator] = {"true_labels": [], "predicted_labels": []}

        # 计算未来收益率
        future_returns = calculate_future_return(stock_data, trade_date)

        # 计算每个指标的准确性
        for indicator, recommendation in indicator_signals.items():
            best_future_days = max(future_returns, key=lambda d: future_returns[d] if future_returns[d] is not None else -1)

            if future_returns[best_future_days] is not None:
                if recommendation == '买入' and future_returns[best_future_days] > 0.02:  # 2% 收益率阈值
                    accuracy_data[indicator]["true_labels"].append(1)
                    accuracy_data[indicator]["predicted_labels"].append(1)
                elif recommendation == '卖出' and future_returns[best_future_days] < -0.02:  # -2% 收益率阈值
                    accuracy_data[indicator]["true_labels"].append(1)
                    accuracy_data[indicator]["predicted_labels"].append(-1)
                else:
                    accuracy_data[indicator]["true_labels"].append(0)
                    accuracy_data[indicator]["predicted_labels"].append(0)

    # 计算各个指标的准确率
    print("各指标的准确率：")
    for indicator, data in accuracy_data.items():
        if data["true_labels"]:
            accuracy = accuracy_score(data["true_labels"], np.sign(data["predicted_labels"]))
            print(f"{indicator} 指标的准确率: {accuracy:.2%}")
        else:
            print(f"警告: {indicator} 没有足够的交易数据进行准确率计算。")

    return accuracy_data


def calculate_indicator_weights(accuracy_data, stock_data):
    """
    根据各个指标的回测准确率计算权重比例
    :param accuracy_data: 各技术指标的准确性数据
    :param stock_data: 股票历史数据（包含收盘价、波动率等）
    :return: 计算后的 indicator_weights
    """
    print("Stock Data Columns:", stock_data.columns)  # 调试信息

    # 确保 volatility 存在
    if 'volatility' not in stock_data.columns:
        print("Volatility not found, calculating it now...")
        stock_data["returns"] = stock_data["close"].pct_change()
        stock_data["volatility"] = stock_data["returns"].rolling(window=20).std()
        stock_data["volatility"] = stock_data["volatility"].fillna(0)

    # 计算市场环境（趋势 or 震荡）
    avg_volatility = stock_data["volatility"].mean()
    current_volatility = stock_data['volatility'].iloc[-1]

    if current_volatility > avg_volatility * 1.2:
        market_condition = "震荡市场"
    else:
        market_condition = "趋势市场"

    # 计算各指标的准确率
    indicator_accuracies = {}
    for indicator, data in accuracy_data.items():
        if data["true_labels"]:
            accuracy = accuracy_score(data["true_labels"], np.sign(data["predicted_labels"]))
            indicator_accuracies[indicator] = accuracy

    # 归一化，使所有准确率加起来等于 1
    total_accuracy = sum(indicator_accuracies.values())
    if total_accuracy == 0:
        normalized_accuracies = {indicator: 1 / len(indicator_accuracies) for indicator in indicator_accuracies}
    else:
        normalized_accuracies = {indicator: acc / total_accuracy for indicator, acc in indicator_accuracies.items()}

    # 生成新的 indicator_weights
    indicator_weights = {market_condition: {}}
    for indicator, normalized_weight in normalized_accuracies.items():
        base_weights = {'买入': 0.4, '卖出': 0.4, '观望': 0.2}  # 默认比例
        adjusted_weights = {k: v * normalized_weight for k, v in base_weights.items()}
        indicator_weights[market_condition][indicator] = adjusted_weights

    return indicator_weights

def generate_stock_weights(stock_list):
    """
    针对不同股票，计算各自的指标建议比例
    :param stock_list: 股票实例列表
    :return: 每只股票的定制化指标权重
    """
    stock_weights = {}

    for stock in stock_list:
        print(f"\n正在计算 {stock.ticker} 的指标权重...")

        # 运行回测，获取该股票的指标准确性
        accuracy_data = backtest(stock)

        # 生成该股票的指标权重
        stock_data = stock.data_fetcher.fetch_data()
        indicator_weights = calculate_indicator_weights(accuracy_data, stock_data)

        # 存入结果
        stock_weights[stock.ticker] = indicator_weights

    return stock_weights


if __name__ == "__main__":
    stock_tickers = ['sz.300377']  # 示例股票列表
    start_date = '2021-01-01'  # 统一回测起始时间
    end_date = '2025-04-02'  # 统一回测结束时间
    window_list = [6, 24]  # RSI 窗口

    stock_list = [
        StockAnalysis(ticker, start_date, end_date, forward_days=365, initial_cash=100000,
                      rsi_window_list=window_list,
                      fast_period=12, slow_period=26, signal_period=9)
        for ticker in stock_tickers
    ]

    # 计算所有股票的定制化指标建议比例
    stock_weights = generate_stock_weights(stock_list)

    # 输出最终的权重配置
    for ticker, weights in stock_weights.items():
        print(f"\n股票 {ticker} 的最终指标建议比例：")
        print(weights)
