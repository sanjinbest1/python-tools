import yfinance as yf

import baostock as bs
import pandas as pd

class DataFetcher:
    def __init__(self, ticker, start_date, end_date):
        """
        初始化数据获取器

        参数:
        ticker (str): 股票代码，如'AAPL'、'GOOG'
        start_date (str): 开始日期，格式'YYYY-MM-DD'
        end_date (str): 结束日期，格式'YYYY-MM-DD'
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

    def fetch_data(self):
        """
        从yfinance获取股票数据

        返回:
        pd.DataFrame: 包含股票数据的DataFrame
        """
        stock_data = yf.download(self.ticker, start=self.start_date, end=self.end_date)

        return stock_data

    def fetch_data_from_baostock(self):
        """
        使用baostock从A股市场获取指定股票的历史数据
        :param stock_code: 股票代码，如 'sh.600000'（注意沪市股票使用 'sh'，深市股票使用 'sz'）
        :param start_date: 开始日期，格式为 'YYYY-MM-DD'
        :param end_date: 结束日期，格式为 'YYYY-MM-DD'
        :return: Pandas DataFrame，包含指定日期范围内的股票数据
        """
        # 登录baostock
        lg = bs.login()
        if lg.error_code != '0':
            print(f"登录失败：{lg.error_msg}")
            return None

        # 查询股票历史数据
        rs = bs.query_history_k_data_plus(
            self.ticker,
            "date,open,high,low,close,volume,amount",
            start_date=self.start_date,
            end_date=self.end_date,
            frequency="d",  # 日线数据
            adjustflag="3"  # 前复权
        )

        # 将返回的数据转化为DataFrame
        data_list = []
        while rs.error_code == '0' and rs.next():
            data_list.append(rs.get_row_data())

        if data_list:
            data = pd.DataFrame(data_list, columns=rs.fields)
            data['date'] = pd.to_datetime(data['date'])
            data = data.set_index('date')
        else:
            print(f"没有数据: {self.ticker}")
            data = None

        # 登出baostock
        bs.logout()

        # 确保 'close' 列是数值类型
        data['close'] = pd.to_numeric(data['close'], errors='coerce')

        return data
