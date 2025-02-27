from stock.data.stock_analysis import StockAnalysis
from stock.indicator.rsi import (plot_multiple_rsi,calculate_rsi_for_multiple_windows,
                                 generate_operation_suggestion)
def analyze(stock):
    """
    执行完整的分析流程：获取数据、计算RSI、绘制图表并生成建议
    """
    print(f"正在分析股票: {stock.ticker}")

    #计算RSI
    rsi_values = calculate_rsi_for_multiple_windows(stock.stock_data, stock.rsi_window_list)

    #绘制图表
    plot_multiple_rsi(stock.stock_data, rsi_values, stock.rsi_window_list)

    #生成建议
    recommendation = generate_operation_suggestion(rsi_values, stock.rsi_window_list)
    print(f"操作建议:")
    print(recommendation)


# 示例：创建StockAnalysis对象并执行分析
if __name__ == '__main__':
    ticker = 'sh.600570'  # 股票代码
    start_date = '2024-08-01'
    end_date = '2025-02-26'
    window_list = [7, 14, 28]

    stock = StockAnalysis(ticker, start_date, end_date,window_list)
    analyze(stock)
