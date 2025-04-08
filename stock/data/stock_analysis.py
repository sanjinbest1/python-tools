from stock.data.data_fetcher import DataFetcher


class StockAnalysis:

    def __init__(self, ticker, start_date, end_date,stock_data_forward_days = 0):
        """
        初始化股票分析对象

        参数:
        ticker (str): 股票代码，如'AAPL'、'GOOG'one
        start_date (str): 开始日期，格式'YYYY-MM-DD'
        end_date (str): 结束日期，格式'YYYY-MM-DD'
        rsi_window (int): RSI计算的窗口期，默认为14
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

        self.data_fetcher = DataFetcher(ticker, start_date, end_date,stock_data_forward_days)

        self.last_price=None

        self.stock_data_forward_days = stock_data_forward_days
