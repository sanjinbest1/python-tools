import datetime
from datetime import timedelta
from stock.data.stock_analysis import StockAnalysis
from stock.indicator.rsi import *
from stock.indicator.macd import *
from stock.indicator.bollinger_bands import *
from stock.indicator.obv import *
from stock.indicator.vwap import *
from stock.indicator.stochastic_rsi import *
from stock.indicator.adx import *
from stock.indicator.atr import *
from stock.indicator.keltner_channel import *

def calculate_indicators(stock_data):
    """
    计算所有指标并返回建议。
    """
    return {
        'rsi': generate_operation_suggestion(calculate_rsi_for_multiple_windows(stock_data)),
        'macd': generate_macd_signal(*calculate_macd(stock_data['close'])),
        'bollinger': generate_bollinger_operations(generate_bollinger_signals(calculate_bollinger_bands(stock_data))),
        'obv': generate_obv_operation_suggestion(calculate_obv(stock_data), stock_data),
        'vwap': generate_vwap_operation_suggestion(stock_data, calculate_vwap(stock_data)),
        'stochastic_rsi': generate_stochastic_rsi_operation_suggestion(calculate_stochastic_rsi(stock_data)),
        'adx': generate_adx_operation_suggestion(calculate_adx_safe(stock_data)),
        'atr': generate_atr_operation_suggestion(calculate_atr(stock_data)),
        'keltner': generate_keltner_channel_operation_suggestion(calculate_keltner_channel(stock_data))
    }

def strategy_with_reason(name, logic_desc, signals, decision):
    """
    打印策略名称、逻辑说明、指标判断和最终建议
    """
    print(f"\n【{name}】")
    print(f"策略逻辑：{logic_desc}")
    for indicator, signal in signals.items():
        print(f" - {indicator.upper()}：{signal}")
    print(f"策略建议：{decision}")
    return decision

def strategy_1(stock_data, indicators):
    """
    趋势确认与逆势反弹组合（RSI、ADX、Stochastic RSI）
    """
    rsi = indicators['rsi']
    adx = indicators['adx']
    stochastic = indicators['stochastic_rsi']
    logic = "当RSI显示超卖，ADX显示趋势增强，Stochastic RSI确认超卖区间时，判断为可能的低点反转机会。"

    if rsi == "买入" and adx == "买入" and stochastic == "买入":
        return strategy_with_reason("趋势确认与反弹", logic, {"rsi": rsi, "adx": adx, "stochastic_rsi": stochastic}, "买入")
    elif rsi == "卖出" or adx == "卖出":
        return strategy_with_reason("趋势确认与反弹", logic, {"rsi": rsi, "adx": adx, "stochastic_rsi": stochastic}, "卖出")
    else:
        return strategy_with_reason("趋势确认与反弹", logic, {"rsi": rsi, "adx": adx, "stochastic_rsi": stochastic}, "观望")

def strategy_2(stock_data, indicators):
    """
    反弹确认与波动性保护组合（布林带、Keltner、ATR）
    """
    boll = indicators['bollinger']
    keltner = indicators['keltner']
    atr = indicators['atr']
    logic = "布林带和Keltner同时显示价格偏离下轨，结合ATR判断是否存在较大波动可能带来反弹。"

    if boll == "买入" and keltner == "买入" and atr != "卖出":
        return strategy_with_reason("反弹+波动性保护", logic, {"bollinger": boll, "keltner": keltner, "atr": atr}, "买入")
    else:
        return strategy_with_reason("反弹+波动性保护", logic, {"bollinger": boll, "keltner": keltner, "atr": atr}, "观望")

def strategy_3(stock_data, indicators):
    """
    动量与流动性组合（VWAP、OBV、MACD）
    """
    vwap = indicators['vwap']
    obv = indicators['obv']
    macd = indicators['macd']
    logic = "VWAP显示价格强势，OBV资金流入，MACD呈现多头排列，三者共振确认短期动量趋势。"

    if vwap == "买入" and obv == "买入" and macd == "买入":
        return strategy_with_reason("动量流动性", logic, {"vwap": vwap, "obv": obv, "macd": macd}, "买入")
    else:
        return strategy_with_reason("动量流动性", logic, {"vwap": vwap, "obv": obv, "macd": macd}, "观望")

def strategy_4(stock_data, indicators):
    """
    风险控制组合（RSI、ADX、ATR）
    """
    rsi = indicators['rsi']
    adx = indicators['adx']
    atr = indicators['atr']
    logic = "若市场强趋势（ADX），且出现超买（RSI），同时波动率仍较大（ATR），提示高位风险卖出。"

    if rsi == "卖出" and adx == "买入" and atr != "卖出":
        return strategy_with_reason("风险控制", logic, {"rsi": rsi, "adx": adx, "atr": atr}, "卖出")
    else:
        return strategy_with_reason("风险控制", logic, {"rsi": rsi, "adx": adx, "atr": atr}, "观望")

def final_advice(stock_data):
    indicators = calculate_indicators(stock_data)

    s1 = strategy_1(stock_data, indicators)
    s2 = strategy_2(stock_data, indicators)
    s3 = strategy_3(stock_data, indicators)
    s4 = strategy_4(stock_data, indicators)

    decisions = [s1, s2, s3, s4]
    buy_count = decisions.count("买入")
    sell_count = decisions.count("卖出")

    print("\n【综合建议】")
    if buy_count >= 2:
        print(f"✔ 当前有 {buy_count} 个策略支持买入，建议：买入")
        return "买入"
    elif sell_count >= 2:
        print(f"✘ 当前有 {sell_count} 个策略支持卖出，建议：卖出")
        return "卖出"
    else:
        print(f"当前无明显共识，建议：观望")
        return "观望"

def analyze(stock, stock_data):
    print(f"\n\n==============================")
    print(f"正在分析股票: {stock.ticker}")
    print("==============================")
    decision = final_advice(stock_data)
    print(f"\n【最终操作建议】：{decision}")
    return decision

def main():
    stocks = ['01810']  # 可换为多个代码循环分析
    end_date = '2025-04-08'
    start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")

    for ticker in stocks:
        stock = StockAnalysis(ticker, start_date, end_date)
        stock_data = stock.data_fetcher.fetch_data()
        analyze(stock, stock_data)

if __name__ == '__main__':
    main()
