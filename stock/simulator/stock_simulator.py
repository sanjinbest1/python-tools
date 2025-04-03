class Simulation:
    """
    模拟交易类，负责执行交易并管理持仓和账户状态。
    """
    MIN_TRADE_QUANTITY = 100  # 最小交易单位（100股）
    max_profit_ratio = 0.20  # 最大盈利目标（20%）
    min_loss_ratio = 0.05  # 最小亏损限制（5%）

    def __init__(self, initial_capital):
        """
        初始化模拟交易
        :param initial_capital: 初始资金
        """
        if initial_capital is None or initial_capital <= 0:
            raise ValueError("Initial capital must be a positive number.")
        self.initial_capital = initial_capital  # 初始资金
        self.capital = initial_capital  # 当前可用资金
        self.positions = {}  # 持仓信息 {股票代码: 持仓数量}
        self.entry_prices = {}  # 记录每只股票的买入价格 {股票代码: 买入均价}
        self.transactions = []  # 交易记录

    def calculate_buy_ratio(self, current_price):
        """
        计算买入比例
        :param current_price: 当前股票价格
        :return: 买入比例
        """
        available_funds = self.capital
        # 可以考虑使用剩余资金的一部分进行买入，假设为50%的资金进行买入
        buy_ratio = 0.5
        return buy_ratio

    def calculate_sell_ratio(self, symbol, current_price):
        """
        计算卖出比例
        :param symbol: 股票代码
        :param current_price: 当前股票价格
        :return: 卖出比例
        """
        if symbol in self.positions:
            entry_price = self.entry_prices.get(symbol, current_price)
            price_change = (current_price - entry_price) / entry_price

            # 判断是否达到了止盈或止损条件
            if price_change >= self.max_profit_ratio:  # 达到最大盈利目标
                sell_ratio = 0.5  # 卖出50%的股票来锁定部分利润
            elif price_change <= -self.min_loss_ratio:  # 达到最小亏损限制
                sell_ratio = 0.5  # 卖出50%的股票来限制亏损
            else:
                sell_ratio = 0  # 未达到止盈止损标准时不卖出
        else:
            sell_ratio = 0  # 没有持仓时不卖出
        return sell_ratio

    def execute_trade(self, date, symbol, recommendation, price):
        """
        执行交易
        :param date: 交易日期
        :param symbol: 股票代码
        :param recommendation: 交易建议 ('买入', '卖出', '观望')
        :param price: 交易价格
        """

        if recommendation not in ['买入', '卖出']:
            return

        if recommendation == '买入':
            buy_ratio = self.calculate_buy_ratio(price)

            # 计算买入数量，并保证是100的整数倍
            quantity = int((self.capital * buy_ratio // price) // self.MIN_TRADE_QUANTITY * self.MIN_TRADE_QUANTITY)

            if quantity >= self.MIN_TRADE_QUANTITY:  # 确保最少买入100股
                cost = quantity * price
                self.capital -= cost
                self.positions[symbol] = self.positions.get(symbol, 0) + quantity
                # 记录买入均价
                if symbol in self.entry_prices:
                    total_shares = self.positions[symbol]
                    self.entry_prices[symbol] = (self.entry_prices[symbol] * (total_shares - quantity) + price * quantity) / total_shares
                else:
                    self.entry_prices[symbol] = price

                post_balance = self.positions[symbol]
                post_capital = self.capital
                self.transactions.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'buy',
                    'quantity': quantity,
                    'price': price,
                    'cost': cost,
                    'post_balance': post_balance,
                    'post_capital': post_capital
                })

        elif recommendation == '卖出':
            sell_ratio = self.calculate_sell_ratio(symbol, price)

            if symbol in self.positions and self.positions[symbol] >= self.MIN_TRADE_QUANTITY:
                quantity_to_sell = int((self.positions[symbol] * sell_ratio) // self.MIN_TRADE_QUANTITY * self.MIN_TRADE_QUANTITY)

                if quantity_to_sell >= self.MIN_TRADE_QUANTITY:  # 确保最少卖出100股
                    revenue = quantity_to_sell * price
                    self.capital += revenue
                    self.positions[symbol] -= quantity_to_sell

                    # 如果卖完了，清除该股票的买入均价记录
                    if self.positions[symbol] == 0:
                        del self.entry_prices[symbol]

                    post_balance = self.positions[symbol]
                    post_capital = self.capital
                    self.transactions.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'sell',
                        'quantity': quantity_to_sell,
                        'price': price,
                        'revenue': revenue,
                        'post_balance': post_balance,
                        'post_capital': post_capital
                    })

    def get_transactions(self):
        """获取所有交易记录"""
        return self.transactions

    def format_transaction(self, transaction):
        """
        格式化交易记录
        :param transaction: 单条交易记录
        :return: 格式化后的交易记录字符串
        """
        if transaction['action'] == 'buy':
            return (f"日期: {transaction['date']}, 股票代码: {transaction['symbol']}, "
                    f"操作: 买入, 数量: {transaction['quantity']} 股, "
                    f"价格: {transaction['price']} 元, 总金额: {transaction['cost']} 元, "
                    f"操作后持仓: {transaction['post_balance']} 股, 操作后资金: {transaction['post_capital']} 元")
        elif transaction['action'] == 'sell':
            return (f"日期: {transaction['date']}, 股票代码: {transaction['symbol']}, "
                    f"操作: 卖出, 数量: {transaction['quantity']} 股, "
                    f"价格: {transaction['price']} 元, 总金额: {transaction['revenue']} 元, "
                    f"操作后持仓: {transaction['post_balance']} 股, 操作后资金: {transaction['post_capital']} 元")
        else:
            return (f"日期: {transaction['date']}, 股票代码: {transaction['symbol']}, "
                    f"操作: 观望, 无交易发生")

    def get_portfolio_value(self, current_price, symbol):
        """
        计算当前持仓的总价值
        :param current_price: 当前价格
        :param symbol: 股票代码
        :return: 持仓总价值
        """
        portfolio_value = self.capital
        quantity = self.positions.get(symbol, 0)  # 获取当前持仓的数量
        portfolio_value += quantity * current_price  # 将持仓数量和当前价格相乘得到总价值
        return portfolio_value
