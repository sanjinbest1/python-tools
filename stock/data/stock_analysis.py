from stock.data.data_fetcher import DataFetcher
from datetime import datetime, timedelta
from stock.simulator.stock_simulator import Simulation

class StockAnalysis:

    def __init__(self, ticker, start_date, end_date, forward_days = None, backwards_days = None,
                 initial_cash = None, cost = None,
                 rsi_window_list=[5],
                 fast_period=5, slow_period=13, signal_period=5,
                 bollinger_hands_window = 20,bollinger_hands_num_std=2
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
        self.forward_days = forward_days
        self.backwards_days = backwards_days
        self.initial_cash = initial_cash
        self.cost = cost

        # RSI窗口期
        self.rsi_window_list = rsi_window_list

        # MACD参数
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

        self.bollinger_hands_window = bollinger_hands_window
        self.bollinger_hands_num_std = bollinger_hands_num_std

        # 数据获取器
        if forward_days is not None:
            start_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=forward_days)).strftime('%Y-%m-%d')

        self.data_fetcher = DataFetcher(ticker, start_date, end_date)

        self.simulation = Simulation(initial_cash)

        self.last_price=None
