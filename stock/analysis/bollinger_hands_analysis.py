from stock.data.stock_analysis import StockAnalysis
from stock.indicator.bollinger_bands import *
def analyze(stock):
    """
    执行完整的分析流程：获取数据、计算RSI、绘制图表并生成建议
    """
    print(f"正在分析股票: {stock.ticker}")

    #计算bollinger_hands
    calculate_bollinger_bands(stock.stock_data, stock.bollinger_hands_window,stock.bollinger_hands_num_std)

    generate_bollinger_signals(stock.stock_data)

    #绘制图表
    plot_bollinger_bands(stock.stock_data)

    #生成建议
    recommendation = generate_bollinger_operations(stock.stock_data)
    print(f"操作建议:")
    print(recommendation)


# 示例：创建StockAnalysis对象并执行分析
if __name__ == '__main__':
    ticker = 'sh.600570'  # 股票代码
    start_date = '2024-08-01'
    end_date = '2025-02-27'
    window_list = [7, 14, 28]

    stock = StockAnalysis(ticker, start_date, end_date)
    analyze(stock)
