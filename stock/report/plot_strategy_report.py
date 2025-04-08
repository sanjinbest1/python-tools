import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def plot_strategy_report(stock_data, signal_series, market_type_series, title="策略图形报告"):
    """
    绘制策略图形报告：
    - 收盘价趋势线
    - 买卖信号点
    - 市场类型背景
    """
    fig, ax = plt.subplots(figsize=(16, 8))
    stock_data['close'].plot(ax=ax, label='收盘价', color='black', linewidth=1.5)

    # 添加信号点
    signal_colors = {
        '买入': 'green',
        '谨慎买入': 'lightgreen',
        '卖出': 'red',
        '强烈卖出': 'darkred'
    }

    for signal_type, color in signal_colors.items():
        signal_dates = signal_series[signal_series == signal_type].index
        signal_prices = stock_data.loc[signal_dates, 'close']
        ax.scatter(signal_dates, signal_prices, label=signal_type,
                   color=color, marker='^' if '买入' in signal_type else 'v', s=100)

    # 市场类型背景色
    for market_type, color in [('趋势', '#cce5ff'), ('震荡', '#f0f0f0')]:
        ranges = get_market_type_ranges(market_type_series, market_type)
        for start, end in ranges:
            ax.axvspan(start, end, color=color, alpha=0.2)

    ax.set_title(title)
    ax.set_ylabel("价格")
    ax.legend()
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def get_market_type_ranges(market_type_series, target_type):
    """
    提取连续市场类型区间
    返回区间 (start_date, end_date)
    """
    ranges = []
    current_start = None

    for date, value in market_type_series.items():
        if value == target_type:
            if current_start is None:
                current_start = date
        elif current_start is not None:
            ranges.append((current_start, date))
            current_start = None

    if current_start is not None:
        ranges.append((current_start, market_type_series.index[-1]))

    return ranges
