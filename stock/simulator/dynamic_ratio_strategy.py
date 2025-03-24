class DynamicRatioStrategy:
    """
    动态比例策略类，先根据工具提供的买入或卖出建议，再计算操作的比例。
    """

    def __init__(self, base_buy_ratio=0.2, base_sell_ratio=0.2):
        """
        初始化动态比例策略
        :param base_buy_ratio: 基础买入比例 (默认 20%)
        :param base_sell_ratio: 基础卖出比例 (默认 20%)
        """
        self.base_buy_ratio = base_buy_ratio
        self.base_sell_ratio = base_sell_ratio

    def market_based_ratio(self, market_factor):
        """
        根据市场条件动态调整买入和卖出比例
        :param market_factor: 市场条件因子 (如波动率、RSI 等)
        :return: 动态买入比例和卖出比例
        """
        if market_factor > 0.7:  # 市场风险较高
            return self.base_buy_ratio * 0.5, self.base_sell_ratio * 1.0
        elif market_factor < 0.3:  # 市场风险较低
            return self.base_buy_ratio * 1.5, self.base_sell_ratio * 0.5
        else:  # 市场风险适中
            return self.base_buy_ratio, self.base_sell_ratio

    def profit_loss_based_ratio(self, account_profit):
        """
        根据账户盈亏动态调整买入和卖出比例
        :param account_profit: 账户当前盈亏金额
        :return: 动态买入比例和卖出比例
        """
        if account_profit > 0:  # 账户盈利
            return self.base_buy_ratio * 0.8, self.base_sell_ratio * 1.2
        elif account_profit < 0:  # 账户亏损
            return self.base_buy_ratio * 1.2, self.base_sell_ratio * 0.8
        else:  # 账户盈亏平衡
            return self.base_buy_ratio, self.base_sell_ratio

    def calculate_operation_ratio(self, trade_signal, account_profit, market_factor, w1=0.5, w2=0.5):
        """
        根据交易建议、市场条件和账户盈亏计算买入和卖出比例
        :param trade_signal: 交易建议 ('buy', 'sell', 'hold')
        :param account_profit: 账户当前盈亏金额
        :param market_factor: 市场条件因子 (如波动率、RSI 等)
        :param w1: 市场条件策略的权重
        :param w2: 账户盈亏策略的权重
        :return: 最终买入比例和卖出比例
        """
        # 获取市场条件策略的比例
        buy_ratio_1, sell_ratio_1 = self.market_based_ratio(market_factor)

        # 获取账户盈亏策略的比例
        buy_ratio_2, sell_ratio_2 = self.profit_loss_based_ratio(account_profit)

        # 根据交易建议调整比例
        if trade_signal == '买入':
            final_buy_ratio = w1 * buy_ratio_1 + w2 * buy_ratio_2
            final_sell_ratio = 0  # 买入时卖出比例为 0
        elif trade_signal == '卖出':
            final_sell_ratio = w1 * sell_ratio_1 + w2 * sell_ratio_2
            final_buy_ratio = 0  # 卖出时买入比例为 0
        else:  # 持仓观望
            final_buy_ratio = 0
            final_sell_ratio = 0

        # 确保比例在合理范围内 (0到1之间)
        final_buy_ratio = max(0.0, min(1.0, final_buy_ratio))  # 最低 0%，最高 100%
        final_sell_ratio = max(0.0, min(1.0, final_sell_ratio))

        return final_buy_ratio, final_sell_ratio
