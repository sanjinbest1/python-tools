import yfinance as yf
import baostock as bs
import akshare as ak
import pandas as pd

class DataFetcher:
    def __init__(self, ticker, start_date, end_date):
        """
        初始化数据获取器
        :param ticker: 股票代码（美股: "AAPL"，A股: "sh.600000"，港股: "00700"）
        :param start_date: 开始日期（YYYY-MM-DD）
        :param end_date: 结束日期（YYYY-MM-DD）
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

    def fetch_data(self):
        """
        根据股票代码自动选择数据源，返回统一格式的股票数据。
        """
        if self.ticker.isdigit():  # 纯数字，可能是港股
            return self.fetch_data_hk()
        elif self.ticker.startswith(("sh.", "sz.")):  # A股代码
            return self.fetch_data_cn()
        else:  # 默认美股
            return self.fetch_data_us()

    def fetch_data_us(self):
        """从 yfinance 获取美股数据"""
        stock_data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
        stock_data = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']]
        stock_data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
        stock_data.index.name = 'date'
        stock_data['amount'] = None  # 美股没有交易额数据
        return stock_data

    def fetch_data_cn(self):
        """从 baostock 获取A股数据"""
        bs.login()
        rs = bs.query_history_k_data_plus(
            self.ticker,
            "date,open,high,low,close,volume,amount",
            start_date=self.start_date,
            end_date=self.end_date,
            frequency="d",
            adjustflag="3"
        )
        data_list = []
        while rs.error_code == '0' and rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            print(f"没有A股数据: {self.ticker}")
            return None

        data = pd.DataFrame(data_list, columns=rs.fields)
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)

        # 转换数据格式
        for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        bs.logout()
        return data

    def fetch_data_hk(self):
        """从 akshare 获取港股数据"""
        data = ak.stock_hk_hist(symbol=self.ticker, period="daily", start_date=self.start_date.replace("-", ""), end_date=self.end_date.replace("-", ""), adjust="qfq")

        if data is None or data.empty:
            print(f"没有港股数据: {self.ticker}")
            return None

        # 重命名字段，使其与 A股 / 美股 统一
        data.rename(columns={
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount"
        }, inplace=True)

        # 转换数据类型
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)

        for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        return data

