from stock.data.data_fetcher import DataFetcher

class StockAnalysis:

    def __init__(self, ticker, start_date, end_date, cost = None,
                 rsi_window_list=None,
                 fast_period=5, slow_period=13, signal_period=5

                 ):
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
        self.cost = cost

        # RSI窗口期
        self.rsi_window_list = rsi_window_list

        # MACD参数
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

        # 数据获取器
        self.data_fetcher = DataFetcher(ticker, start_date, end_date)
        self.stock_data = self.data_fetcher.fetch_data_from_baostock()
