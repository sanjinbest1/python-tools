from stock.data.stock_analysis import StockAnalysis
from stock.indicator.macd import *
from pprint import pprint

def analyze(stock):

    # 计算MACD
    macd_dict = calculate_macd(stock.stock_data['close'],
                               fast_period=stock.fast_period, slow_period=stock.slow_period, signal_period=stock.signal_period)

    pprint(macd_dict)

    # 生成操作建议
    recommendation = generate_macd_signal(macd_dict['macd'], macd_dict['signal'], cost=stock.cost)
    print(recommendation)

    # 绘制多个MACD图
    # plot_macd_with_signal(stock.stock_data['close'], macd_dict,
    #                       fast_period=stock.fast_period, slow_period=stock.slow_period, signal_period=stock.signal_period)


# 示例：创建StockAnalysis对象并执行分析
if __name__ == '__main__':
    ticker = 'sh.600570'  # 股票代码
    start_date = '2024-08-01'
    end_date = '2025-02-26'

    stock = StockAnalysis(ticker, start_date, end_date,cost=31,fast_period=5, slow_period=13, signal_period=5)
    analyze(stock)
