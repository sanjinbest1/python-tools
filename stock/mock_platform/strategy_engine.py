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

# ==== 权重表（可动态调整） ====
indicator_weights = {
    'rsi': {'买入': 0.05, '卖出': 0.05, '观望': 0.025},
    'macd': {'买入': 0.05, '卖出': 0.05, '观望': 0.025},
    'bollinger': {'买入': 0.05, '卖出': 0.05, '观望': 0.025},
    'obv': {'买入': 0.04, '卖出': 0.04, '观望': 0.02},
    'vwap': {'买入': 0.04, '卖出': 0.04, '观望': 0.02},
    'stochastic_rsi': {'买入': 0.04, '卖出': 0.04, '观望': 0.02},
    'adx': {'买入': 0.05, '卖出': 0.05, '观望': 0.025},
    'atr': {'买入': 0.05, '卖出': 0.05, '观望': 0.025},
    'keltner': {'买入': 0.045, '卖出': 0.045, '观望': 0.0225},
}

# ==== 动态调整权重 ====
def adjust_weights_for_market(market_type, indicator_weights):
    adjusted_weights = indicator_weights.copy()

    if market_type == "趋势市":
        # 增加趋势类指标的权重
        adjusted_weights['rsi']['买入'] *= 1.2
        adjusted_weights['macd']['买入'] *= 1.3
        adjusted_weights['adx']['买入'] *= 1.5
        # 减少震荡类指标的权重
        adjusted_weights['bollinger']['观望'] *= 0.8
        adjusted_weights['keltner']['观望'] *= 0.8
    elif market_type == "震荡市":
        # 增加震荡市相关指标的权重
        adjusted_weights['rsi']['买入'] *= 0.8
        adjusted_weights['macd']['买入'] *= 0.7
        adjusted_weights['atr']['卖出'] *= 1.5
        adjusted_weights['bollinger']['买入'] *= 1.2
        adjusted_weights['keltner']['买入'] *= 1.2
    else:  # 中性市
        # 中性市场权重保持均衡
        pass

    # 确保总权重为1
    total_weight = sum([sum(w.values()) for w in adjusted_weights.values()])
    for ind in adjusted_weights:
        for action in adjusted_weights[ind]:
            adjusted_weights[ind][action] /= total_weight

    return adjusted_weights

# ==== Step 1: 指标计算 ====
def calculate_indicators(stock_data):
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

# ==== Step 2: 市场类型识别 ====
def detect_market_type(stock_data):
    adx_values = calculate_adx_safe(stock_data)
    atr_values = calculate_atr(stock_data)
    bb = calculate_bollinger_bands(stock_data)
    bollinger_width = (bb['high'] - bb['low']) / stock_data['close']

    recent_adx = adx_values.iloc[-1] if not adx_values.empty else 20
    recent_atr = atr_values.iloc[-1] if not atr_values.empty else 0.01
    recent_bw = bollinger_width.iloc[-1] if not bollinger_width.empty else 0.05

    if recent_adx > 25 and recent_bw > 0.06:
        return "趋势市"
    elif recent_bw < 0.04 and recent_adx < 20:
        return "震荡市"
    else:
        return "中性市"

# ==== Step 3: 静态加权建议 ====
def weighted_decision(indicators, indicator_weights):
    buy_score, sell_score, hold_score = 0, 0, 0
    for ind, signal in indicators.items():
        weight = indicator_weights[ind]
        if signal == "买入":
            buy_score += weight['买入']
        elif signal == "卖出":
            sell_score += weight['卖出']
        else:
            hold_score += weight['观望']

    diff = buy_score - sell_score
    explain = f"买入得分={buy_score:.2f}，卖出得分={sell_score:.2f}，观望得分={hold_score:.2f}"

    if diff > 0.08:
        return "强烈买入", explain
    elif diff > 0.02:
        return "谨慎买入", explain
    elif diff < -0.08:
        return "强烈卖出", explain
    elif diff < -0.02:
        return "谨慎卖出", explain
    else:
        return "观望", explain

# ==== Step 4: 策略组合判断 ====
def grouped_strategies(indicators):
    strategy_results = []
    reasons = []

    # 策略1：趋势确认与反弹
    if indicators['rsi'] == "买入" and indicators['adx'] == "买入" and indicators['stochastic_rsi'] == "买入":
        strategy_results.append("买入")
        reasons.append("策略1确认低点反转信号成立")
    elif indicators['rsi'] == "卖出" or indicators['adx'] == "卖出":
        strategy_results.append("卖出")
        reasons.append("策略1提示趋势减弱或超买")

    # 策略2：波动+布林+Keltner
    if indicators['bollinger'] == "买入" and indicators['keltner'] == "买入" and indicators['atr'] != "卖出":
        strategy_results.append("买入")
        reasons.append("策略2：低波动区域预示反弹机会")

    # 策略3：动量（MACD+VWAP+OBV）
    if indicators['macd'] == "买入" and indicators['vwap'] == "买入" and indicators['obv'] == "买入":
        strategy_results.append("买入")
        reasons.append("策略3：资金动能共振")

    # 策略4：风险控制
    if indicators['rsi'] == "卖出" and indicators['adx'] == "买入" and indicators['atr'] != "卖出":
        strategy_results.append("卖出")
        reasons.append("策略4：高波动+强趋势+超买风险")

    buy_count = strategy_results.count("买入")
    sell_count = strategy_results.count("卖出")

    if buy_count >= 2:
        return "强烈买入", reasons
    elif buy_count == 1:
        return "谨慎买入", reasons
    elif sell_count >= 2:
        return "强烈卖出", reasons
    elif sell_count == 1:
        return "谨慎卖出", reasons
    else:
        return "观望", reasons

# ==== Step 5: 总体融合建议 ====
def final_suggestion(indicators, market_type, indicator_weights):
    adjusted_weights = adjust_weights_for_market(market_type, indicator_weights)
    weighted, weighted_reason = weighted_decision(indicators, adjusted_weights)
    grouped, group_reasons = grouped_strategies(indicators)

    explanation = [f"【市场判断】：当前为 {market_type}",
                   f"【加权建议】：{weighted}（{weighted_reason}）",
                   f"【策略建议】：{grouped}"]
    explanation += [f" - {r}" for r in group_reasons]

    # 综合判断机制
    scores = {
        "强烈买入": 2, "谨慎买入": 1,
        "观望": 0,
        "谨慎卖出": -1, "强烈卖出": -2
    }

    total_score = scores[weighted] + scores[grouped]
    if total_score >= 3:
        final = "强烈买入"
    elif total_score == 2:
        final = "谨慎买入"
    elif total_score == 1 or total_score == 0:
        final = "观望"
    elif total_score == -1:
        final = "谨慎卖出"
    else:
        final = "强烈卖出"

    return final, explanation

def analyze(stock, stock_data):
    print(f"\n==============================")
    print(f"正在分析股票: {stock.ticker}")
    indicators = calculate_indicators(stock_data)
    market_type = detect_market_type(stock_data)
    final_decision, reasons = final_suggestion(indicators, market_type, indicator_weights)

    print(f"\n【最终操作建议】：{final_decision}")
    print("\n【建议理由】：")
    for r in reasons:
        print(r)

    return final_decision


def main():
    stocks = ['sh.600570']
    end_date = '2025-04-08'
    start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")

    for ticker in stocks:
        stock = StockAnalysis(ticker, start_date, end_date)
        stock_data = stock.data_fetcher.fetch_data()

        analyze(stock, stock_data)

if __name__ == '__main__':
    main()
