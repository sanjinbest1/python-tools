import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from stock.data.data_fetcher import DataFetcher
from stock.analysis.combined_rate_analysis import analyze
from stock.data.stock_analysis import StockAnalysis
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np

# 设置 matplotlib 支持中文，使用 macOS 系统自带字体
plt.rcParams['font.sans-serif'] = ['Heiti TC']
plt.rcParams['axes.unicode_minus'] = False

def backtest(stock):
    """
    进行回测
    :param stock_code: 股票代码
    :param start_date: 回测开始日期，格式：YYYYMMDD
    :param end_date: 回测结束日期，格式：YYYYMMDD
    """

    stock_data = stock.data_fetcher.fetch_data_from_baostock()

    # 获取回测时间段内的交易日
    trade_dates = stock_data[datetime.strptime(stock.start_date, '%Y-%m-%d'):].index

    recommendations = []
    for trade_date in trade_dates:
        # 计算交易日前半年的日期
        half_year_ago_date = (trade_date - timedelta(days=stock.forward_days)).strftime('%Y-%m-%d')
        # 获取交易日前半年的数据，并创建副本
        data_for_calculation = stock_data[half_year_ago_date: trade_date.strftime('%Y-%m-%d')].copy()
        if len(data_for_calculation) > 20:  # 确保有足够的数据进行计算
            recommendation = analyze(stock, data_for_calculation)
            recommendations.append((trade_date, recommendation))
        else:
            recommendations.append((trade_date, '观望'))

    # 筛选出开始和结束日期内的数据
    start = datetime.strptime(stock.start_date, '%Y-%m-%d')
    end = datetime.strptime(stock.end_date, '%Y-%m-%d')
    filtered_stock_data = stock_data[(stock_data.index >= start) & (stock_data.index <= end)]
    filtered_recommendations = [(date, rec) for date, rec in recommendations if start <= date <= end]

    # 绘制股票价格图并标记操作建议，放大图形尺寸
    plt.figure(figsize=(25, 9))
    x_indices = np.arange(len(filtered_stock_data))
    plt.plot(x_indices, filtered_stock_data['close'], label='收盘价')
    buy_shown = False
    sell_shown = False
    for date, recommendation in filtered_recommendations:
        index = filtered_stock_data.index.get_loc(date)
        if recommendation == '买入':
            if not buy_shown:
                label = '买入'
                buy_shown = True
            else:
                label = ""
            plt.scatter(index, filtered_stock_data.loc[date, 'close'], color='green', marker='^', label=label)
        elif recommendation == '卖出':
            if not sell_shown:
                label = '卖出'
                sell_shown = True
            else:
                label = ""
            plt.scatter(index, filtered_stock_data.loc[date, 'close'], color='red', marker='v', label=label)

    plt.title(f'{stock.ticker} 回测结果')
    plt.xlabel('日期')
    plt.ylabel('收盘价')
    plt.legend()
    plt.grid(True)

    # 设置 X 轴主刻度定位器，按 30 个平均分
    num_ticks = 30
    tick_locs = np.linspace(0, len(filtered_stock_data) - 1, num_ticks, dtype=int)
    tick_dates = [filtered_stock_data.index[i].strftime('%m%d') for i in tick_locs]
    plt.xticks(tick_locs, tick_dates)

    plt.show()

    # 输出操作建议
    print("操作建议：")
    for date, recommendation in recommendations:
        print(f"{date.strftime('%Y%m%d')}: {recommendation}")


if __name__ == "__main__":

    stock_ticker = 'SH.600446'  # 示例股票代码，将 ticker 重命名为 stock_ticker
    # start_date = '2025-03-20'  # 示例回测开始日期
    start_date = '2025-01-01'  # 示例回测开始日期
    end_date = '2025-03-21'  # 示例回测结束日期
    window_list = [6, 24]  # RSI的多个窗口

    stock = StockAnalysis(stock_ticker, start_date, end_date, forward_days=180,
                          rsi_window_list=window_list,
                          fast_period=12, slow_period=26, signal_period=9)
    backtest(stock)
