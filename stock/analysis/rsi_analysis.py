from stock.data.data_fetcher import DataFetcher
import pandas as pd
from stock.indicator.rsi import (plot_multiple_rsi,calculate_rsi_for_multiple_windows,
                                 generate_operation_suggestion)

class StockAnalysis:
    def __init__(self, ticker, start_date, end_date, rsi_window_list):
        """
        初始化股票分析对象

        参数:
        ticker (str): 股票代码，如'AAPL'、'GOOG'
        start_date (str): 开始日期，格式'YYYY-MM-DD'
        end_date (str): 结束日期，格式'YYYY-MM-DD'
        rsi_window (int): RSI计算的窗口期，默认为14
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.rsi_window_list = rsi_window_list

    def calculate_rsi(self):
        """
        计算RSI指标


        返回:
        pd.Series: 计算出的RSI值
        """

        # 确保 'close' 列是数值类型
        self.stock_data['close'] = pd.to_numeric(self.stock_data['close'], errors='coerce')

        return calculate_rsi_for_multiple_windows(self.stock_data, self.rsi_window_list)

    def plot_results(self):
        """
        绘制股票价格和RSI图表
        """
        plot_multiple_rsi(self.stock_data, self.rsi_values, self.rsi_window_list)

    def generate_recommendations(self):
        """
        基于RSI结果生成股票操作建议

        返回:
        str: 操作建议
        """
        return generate_operation_suggestion(self.rsi_values, self.rsi_window_list)

    def analyze(self):
        """
        执行完整的分析流程：获取数据、计算RSI、绘制图表并生成建议
        """
        self.data_fetcher = DataFetcher(ticker, start_date, end_date)
        self.stock_data = self.data_fetcher.fetch_data_from_baostock()
        self.rsi_values = self.calculate_rsi()

        print(f"正在分析股票: {self.ticker}")
        self.plot_results()
        recommendation = self.generate_recommendations()
        print(f"操作建议:")
        print(recommendation)


# 示例：创建StockAnalysis对象并执行分析
if __name__ == '__main__':
    ticker = 'sh.600570'  # 股票代码
    start_date = '2024-08-01'
    end_date = '2025-02-26'
    window_list = [7, 14, 28]

    stock_analysis = StockAnalysis(ticker, start_date, end_date, window_list)
    stock_analysis.analyze()
