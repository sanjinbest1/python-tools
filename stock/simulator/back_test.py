import matplotlib.pyplot as plt
from stock.mock_platform.original_strategy_engine import analyze
from stock.data.stock_analysis import StockAnalysis
import numpy as np
from datetime import datetime, timedelta
from stock.simulator.simulation import Simulation

# 设置 matplotlib 支持中文，使用 macOS 系统自带字体
plt.rcParams['font.sans-serif'] = ['Heiti TC']
plt.rcParams['axes.unicode_minus'] = False

def backtest(stock,simulation):
    """
    进行回测
    """

    stock_data = stock.data_fetcher.fetch_data()

    # 获取回测时间段内的交易日
    start_date_dt = datetime.strptime(stock.start_date, '%Y-%m-%d')
    trade_dates = stock_data.loc[start_date_dt:].index

    recommendations = []
    for trade_date in trade_dates:
        # 计算交易日前半年的日期
        half_year_ago_date = (trade_date - timedelta(days=stock.stock_data_forward_days)).strftime('%Y-%m-%d')
        # 获取交易日前半年的数据，并创建副本
        data_for_calculation = stock_data.loc[half_year_ago_date: trade_date.strftime('%Y-%m-%d')].copy()
        if len(data_for_calculation) > 20:  # 确保有足够的数据进行计算
            recommendation = analyze(stock, data_for_calculation)['final_suggestion']
        else:
            recommendation = '观望'

        recommendations.append((trade_date, recommendation))

        # 获取当天的收盘价
        price = stock_data.loc[trade_date, 'close']
        # 执行交易
        simulation.execute_trade(trade_date, stock.ticker, recommendation, price)

        stock.last_price = price

    # 筛选出开始和结束日期内的数据
    start = datetime.strptime(stock.start_date, '%Y-%m-%d')
    end = datetime.strptime(stock.end_date, '%Y-%m-%d')
    filtered_stock_data = stock_data.loc[start:end]
    filtered_recommendations = [(date, rec) for date, rec in recommendations if start <= date <= end]

    # 绘制股票价格图并标记操作建议
    plt.figure(figsize=(25, 9))
    x_indices = np.arange(len(filtered_stock_data))
    plt.plot(x_indices, filtered_stock_data['close'], label='收盘价')

    buy_shown = False
    sell_shown = False
    for date, recommendation in filtered_recommendations:
        index = filtered_stock_data.index.get_loc(date)
        if recommendation in ['买入','强烈买入','谨慎买入']:
            label = '买入' if not buy_shown else ""
            buy_shown = True
            plt.scatter(index, filtered_stock_data.loc[date, 'close'], color='green', marker='^', label=label)
        elif recommendation in ['卖出', '强烈卖出', '谨慎卖出']:
            label = '卖出' if not sell_shown else ""
            sell_shown = True
            plt.scatter(index, filtered_stock_data.loc[date, 'close'], color='red', marker='v', label=label)

    plt.title(f'{stock.ticker} 回测结果')
    plt.xlabel('日期')
    plt.ylabel('收盘价')
    plt.legend()
    plt.grid(True)

    # 设置 X 轴主刻度
    num_ticks = 50
    tick_locs = np.linspace(0, len(filtered_stock_data) - 1, num_ticks, dtype=int)
    tick_dates = [filtered_stock_data.index[i].strftime('%m%d') for i in tick_locs]
    plt.xticks(tick_locs, tick_dates)

    plt.show()

    # 输出操作建议
    print("操作建议：")
    for date, recommendation in recommendations:
        print(f"{date.strftime('%Y%m%d')}: {recommendation}")

if __name__ == "__main__":
    ticker = 'sh.600570'  # 示例股票代码
    end_date = '2025-04-12'
    lookback_years = 1  # 或者3年
    start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=lookback_years * 365)).strftime("%Y-%m-%d")

    # 传入 stock_analysis
    stock = StockAnalysis(ticker, '恒生电子',start_date,end_date, 30)

    simulation = Simulation(100000)

    backtest(stock,simulation)

    # 获取最终持仓价值
    portfolio_value = simulation.get_portfolio_value(stock.last_price, stock.ticker)
    print(f"最终持仓价值: {portfolio_value:.2f}")
    returns = portfolio_value / simulation.initial_capital - 1
    print(f"最终投资回报率: {returns:.2%}")

    transactions = simulation.get_transactions()
    print("交易记录：")
    for t in transactions:
        print(simulation.format_transaction(t))
