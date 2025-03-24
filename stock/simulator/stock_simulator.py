class Simulation:
    """
    模拟交易类，负责执行交易并管理持仓和账户状态。
    """

    def __init__(self, initial_capital):
        """
        初始化模拟交易
        :param initial_capital: 初始资金
        """
        if initial_capital is None or initial_capital <= 0:
            raise ValueError("Initial capital must be a positive number.")
        self.initial_capital = initial_capital  # 初始资金
        self.capital = initial_capital  # 当前可用资金
        self.positions = {}  # 持仓信息，格式为 {股票代码: 持仓数量}
        self.transactions = []  # 交易记录，格式为 [交易信息字典]

    def execute_trade(self, date, symbol, recommendation, price, sell_ratio=0.5):
        """
        执行交易
        :param date: 交易日期
        :param symbol: 股票代码
        :param recommendation: 交易建议 ('买入', '卖出', '观望')
        :param price: 交易价格
        :param sell_ratio: 卖出比例 (0到1之间，默认为0.5，即每次卖出50%的持仓)
        """
        if recommendation == '买入':
            # 假设每次买入固定比例的资金
            quantity = int(self.capital * 0.2 // price)  # 用20%的资金买入，取整
            if quantity > 0:
                cost = quantity * price
                self.capital -= cost
                self.positions[symbol] = self.positions.get(symbol, 0) + quantity
                post_balance = self.positions[symbol]  # 操作后持仓
                post_capital = self.capital  # 操作后资金
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
            if symbol in self.positions and self.positions[symbol] > 0:
                # 减仓逻辑：卖出指定比例的持仓
                quantity_to_sell = int(self.positions[symbol] * sell_ratio)
                if quantity_to_sell > 0:
                    revenue = quantity_to_sell * price
                    self.capital += revenue
                    self.positions[symbol] -= quantity_to_sell  # 减少持仓
                    post_balance = self.positions[symbol]  # 操作后持仓
                    post_capital = self.capital  # 操作后资金
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
        # 如果是 '观望'，则不执行任何操作

    def get_portfolio_value(self, current_price, symbol):
        """
        计算当前持仓的总价值
        :param current_price: 当前价格
        :param symbol: 股票代码
        :return: 持仓总价值
        """
        portfolio_value = self.capital
        quantity = self.positions.get(symbol, 0)
        portfolio_value += quantity * current_price
        return portfolio_value

    def calculate_account_profit(self, current_price):
        """
        计算账户的当前盈亏金额
        :param current_price: 当前价格（用于计算持仓价值）
        :return: 账户当前盈亏金额
        """
        # 计算当前持仓的总价值
        portfolio_value = 0
        for symbol, quantity in self.positions.items():
            portfolio_value += quantity * current_price

        # 当前总资金 = 初始资金 + 当前持仓价值 - 初始持仓价值
        # 由于初始持仓价值无法直接记录，我们用当前总资金减去初始资金来估算盈亏
        # 这里假设 `self.capital` 是当前可用资金，未考虑持仓价值
        # 因此需要重新计算总资金
        total_value = portfolio_value + self.capital  # 当前总资金
        initial_value = self.initial_capital  # 初始资金
        account_profit = total_value - initial_value  # 当前盈亏金额

        return account_profit

    def get_transactions(self):
        """
        获取所有交易记录
        :return: 交易记录列表
        """
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
