import pandas as pd
import matplotlib.pyplot as plt
from stock.data.stock_analysis import StockAnalysis
from stock.indicator.rsi import *
from stock.indicator.macd import *
from stock.indicator.bollinger_bands import *
from stock.analysis.combined_analysis import *
import pandas_market_calendars as mcal

def backtest(stock_ticker, start_date):
    """
    回测股票的交易信号，评估分析工具的准确性。
    :param stock_ticker: 股票代码
    :param start_date: 回测开始日期
    """
    # 获取沪深股市的交易日历
    calendar = mcal.get_calendar('XSHG')
    current_date = pd.Timestamp(start_date)
    results = []  # 存储每次分析的结果

    # 获取沪深股市从开始日期到今天的所有交易日
    trading_days = calendar.valid_days(start_date=current_date, end_date=pd.Timestamp.today())
    stock = None

    while current_date <= pd.Timestamp.today():
        # 检查当前日期是否为交易日
        if current_date in trading_days:
            # 获取当前日期向前1年的数据，同时向后额外获取5天数据
            stock = StockAnalysis(stock_ticker,
                                  (pd.Timestamp(current_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d'),
                                  (pd.Timestamp(current_date) + pd.DateOffset(days=5)).strftime('%Y-%m-%d'))

            # 运行分析
            recommendation = analyze(stock)

            # 获取当前日期的收盘价
            action_price = stock.stock_data.loc[current_date, 'close']

            # 获取3-5天后的收盘价
            future_prices = stock.stock_data.loc[pd.Timestamp(current_date) + pd.DateOffset(days=3):
                                                 pd.Timestamp(current_date) + pd.DateOffset(days=5), 'close']

            # 计算未来价格的平均值
            future_price = future_prices.mean() if not future_prices.empty else None

            # 评估信号正确性
            if recommendation.startswith("买入") and future_price and future_price > action_price:
                correctness = "正确"
            elif recommendation.startswith("卖出") and future_price and future_price < action_price:
                correctness = "正确"
            else:
                correctness = "错误"

            results.append((current_date, recommendation, action_price, future_price, correctness))

        # 移动到下一个日期
        current_date += pd.DateOffset(days=1)

    print(results)

    # 结果转为DataFrame
    results_df = pd.DataFrame(results, columns=['日期', '建议', '操作价格', '未来价格', '准确性'])

    # 计算准确率
    accuracy = results_df['准确性'].value_counts(normalize=True).get("正确", 0) * 100
    print(f"策略准确率: {accuracy:.2f}%")

    # 绘制结果
    plot_backtest_results(results_df, stock.stock_data)

def plot_backtest_results(results_df, stock_data):
    """
    绘制回测结果，包含股票价格、操作建议和正确性。
    """
    plt.figure(figsize=(14, 7))
    plt.plot(stock_data.index, stock_data['close'], label='股票价格', color='blue')

    # 标记买入和卖出点
    for _, row in results_df.iterrows():
        color = 'green' if row['准确性'] == '正确' else 'red'
        if row['建议'].startswith("买入"):
            plt.scatter(row['日期'], row['操作价格'], color=color, marker='^', s=100, label='买入' if '买入' not in plt.gca().get_legend_handles_labels()[1] else "")
        elif row['建议'].startswith("卖出"):
            plt.scatter(row['日期'], row['操作价格'], color=color, marker='v', s=100, label='卖出' if '卖出' not in plt.gca().get_legend_handles_labels()[1] else "")

    plt.legend()
    plt.title('回测结果')
    plt.xlabel('日期')
    plt.ylabel('价格')
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

# 运行回测
if __name__ == '__main__':
    stock_code = 'sh.600570'
    start_backtest_date = '2024-10-01'
    backtest(stock_code, start_backtest_date)
