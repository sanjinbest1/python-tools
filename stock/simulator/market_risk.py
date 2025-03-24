import numpy as np
import pandas as pd

def calculate_stock_market_risk(stock_data, market_data=None, confidence_level=0.95, w_volatility=0.3, w_beta=0.2, w_var=0.2, w_cvar=0.2, w_drawdown=0.1):
    """
    计算股票市场的风险值
    :param stock_data: 股票价格或收益率数据 (Pandas DataFrame 或 Series，包含 'Close' 或 'Returns' 列)
    :param market_data: 市场指数价格或收益率数据 (Pandas DataFrame 或 Series，包含 'Close' 或 'Returns' 列，可选)
    :param confidence_level: 置信水平 (默认 95%，用于 VaR 和 CVaR 计算)
    :param w_volatility: 波动率的权重 (默认 0.3)
    :param w_beta: 贝塔系数的权重 (默认 0.2)
    :param w_var: VaR 的权重 (默认 0.2)
    :param w_cvar: CVaR 的权重 (默认 0.2)
    :param w_drawdown: 最大回撤的权重 (默认 0.1)
    :return: 包含风险指标和综合风险评分的字典
    """
    # 确保输入数据是 Pandas DataFrame 或 Series
    stock_data = pd.DataFrame(stock_data)
    if market_data is not None:
        market_data = pd.DataFrame(market_data)

    # 计算收益率（如果输入是价格数据）
    if 'Close' in stock_data.columns:
        stock_data['Returns'] = stock_data['Close'].pct_change().dropna()
    elif 'Returns' not in stock_data.columns:
        raise ValueError("股票数据必须包含 'Close' 或 'Returns' 列")

    # 如果提供了市场数据，计算市场收益率
    if market_data is not None and 'Close' in market_data.columns:
        market_data['Returns'] = market_data['Close'].pct_change().dropna()
    elif market_data is not None and 'Returns' not in market_data.columns:
        raise ValueError("市场数据必须包含 'Close' 或 'Returns' 列")

    # 初始化风险指标字典
    risk_metrics = {}

    # 1. 波动率 (Volatility)
    daily_volatility = stock_data['Returns'].std()
    annualized_volatility = daily_volatility * np.sqrt(252)  # 假设一年有 252 个交易日
    risk_metrics['Volatility'] = annualized_volatility

    # 2. 贝塔系数 (Beta) - 如果提供了市场数据
    if market_data is not None:
        cov = stock_data['Returns'].cov(market_data['Returns'])
        var_market = market_data['Returns'].var()
        beta = cov / var_market if var_market != 0 else 0
        risk_metrics['Beta'] = beta

    # 3. Value at Risk (VaR) - 参数法
    z_score = {0.95: 1.645, 0.99: 2.326}.get(confidence_level, 1.645)  # 常用分位数
    mean_return = stock_data['Returns'].mean()
    std_return = stock_data['Returns'].std()
    var_parametric = -(mean_return + z_score * std_return)
    risk_metrics['VaR_Parametric'] = var_parametric

    # 4. Value at Risk (VaR) - 历史模拟法
    var_historical = -stock_data['Returns'].quantile(1 - confidence_level)
    risk_metrics['VaR_Historical'] = var_historical

    # 5. 条件风险价值 (CVaR) - 基于历史模拟法
    cvar = stock_data[stock_data['Returns'] <= -var_historical]['Returns'].mean()
    risk_metrics['CVaR'] = cvar

    # 6. 最大回撤 (Max Drawdown)
    cumulative_returns = (1 + stock_data['Returns']).cumprod()
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    risk_metrics['Max_Drawdown'] = max_drawdown

    # 归一化处理
    normalized_metrics = {}
    for metric, value in risk_metrics.items():
        # 将所有指标缩放到 0 到 1 的范围
        min_val = stock_data['Returns'].min() if metric in ['VaR_Parametric', 'VaR_Historical', 'CVaR', 'Max_Drawdown'] else 0
        max_val = stock_data['Returns'].max() if metric in ['VaR_Parametric', 'VaR_Historical', 'CVaR', 'Max_Drawdown'] else 1
