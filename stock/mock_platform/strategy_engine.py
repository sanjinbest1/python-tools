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
import json
import ast

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
        if signal['suggestion'] == "买入":
            buy_score += weight['买入']
        elif signal['suggestion'] == "卖出":
            sell_score += weight['卖出']
        else:
            hold_score += weight['观望']

    diff = buy_score - sell_score
    explain = f"买入得分={buy_score:.3f}，卖出得分={sell_score:.3f}，观望得分={hold_score:.3f}"

    # 新增显著性判断
    if buy_score > 0.12 and buy_score > 2 * sell_score and diff > 0.08:
        return "强烈买入", explain
    elif buy_score > sell_score and diff > 0.03:
        return "谨慎买入", explain
    elif sell_score > 0.12 and sell_score > 2 * buy_score and diff < -0.08:
        return "强烈卖出", explain
    elif sell_score > buy_score and diff < -0.03:
        return "谨慎卖出", explain
    else:
        return "观望", explain


# ==== Step 4: 策略组合判断 ====
def grouped_strategies(indicators):
    strategy_results = []
    reasons = []

    # 策略1：趋势确认与反弹
    if indicators['rsi']['suggestion'] == "买入" and indicators['adx']['suggestion'] == "买入" and indicators['stochastic_rsi']['suggestion'] == "买入":
        strategy_results.append("买入")
        reasons.append("策略1确认低点反转信号成立")
    elif indicators['rsi']['suggestion'] == "卖出" or indicators['adx']['suggestion'] == "卖出":
        strategy_results.append("卖出")
        reasons.append("策略1提示趋势减弱或超买")

    # 策略2：波动+布林+Keltner
    if indicators['bollinger']['suggestion'] == "买入" and indicators['keltner']['suggestion'] == "买入" and indicators['atr']['suggestion'] != "卖出":
        strategy_results.append("买入")
        reasons.append("策略2：低波动区域预示反弹机会")

    # 策略3：动量（MACD+VWAP+OBV）
    if indicators['macd']['suggestion'] == "买入" and indicators['vwap']['suggestion'] == "买入" and indicators['obv']['suggestion'] == "买入":
        strategy_results.append("买入")
        reasons.append("策略3：资金动能共振")

    # 策略4：风险控制
    if indicators['rsi']['suggestion'] == "卖出" and indicators['adx']['suggestion'] == "买入" and indicators['atr']['suggestion'] != "卖出":
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

    # 综合判断机制（改进版）
    scores = {
        "强烈买入": 3, "谨慎买入": 2,
        "观望": 0,
        "谨慎卖出": -2, "强烈卖出": -3
    }

    weighted_score = scores.get(weighted, 0)
    grouped_score = scores.get(grouped, 0)
    total_score = weighted_score + grouped_score

    # 强烈操作必须同时满足策略+加权方向一致 且 至少有一方非常显著
    if weighted == grouped:
        if weighted in ["强烈买入", "强烈卖出"]:
            final = weighted
        elif total_score >= 4:
            final = "强烈买入"
        elif total_score <= -4:
            final = "强烈卖出"
        elif total_score >= 2:
            final = "谨慎买入"
        elif total_score <= -2:
            final = "谨慎卖出"
        else:
            final = "观望"
    else:
        # 分歧时采取更保守策略
        if total_score >= 3:
            final = "谨慎买入"
        elif total_score <= -3:
            final = "谨慎卖出"
        else:
            final = "观望"

    return final, explanation

def generate_strategy_report(indicators):
    report_lines = []
    report_lines.append("📊 策略组分析报告")

    # 策略1：趋势确认与反弹
    if indicators['rsi']['suggestion'] == "买入" and indicators['adx']['suggestion'] == "买入" and indicators['stochastic_rsi']['suggestion'] == "买入":
        report_lines.append("✅ 策略1【趋势反转确认】：满足 RSI、ADX、StochRSI 三重信号，倾向买入。")
    elif indicators['rsi']['suggestion'] == "卖出" or indicators['adx']['suggestion'] == "卖出":
        report_lines.append("⚠️ 策略1【趋势减弱或超买】：RSI/ADX 提示市场可能面临回调。")
    else:
        report_lines.append("➖ 策略1无明显信号。")

    # 策略2：波动+布林+Keltner
    if indicators['bollinger']['suggestion'] == "买入" and indicators['keltner']['suggestion'] == "买入" and indicators['atr']['suggestion'] != "卖出":
        report_lines.append("✅ 策略2【布林+Keltner 缩口反弹】：提示当前处于低波动区，可能反弹。")
    else:
        report_lines.append("➖ 策略2无明显信号。")

    # 策略3：动量
    if indicators['macd']['suggestion'] == "买入" and indicators['vwap']['suggestion'] == "买入" and indicators['obv']['suggestion'] == "买入":
        report_lines.append("✅ 策略3【动能增强】：MACD、VWAP、OBV 联合向好，资金流入明显。")
    else:
        report_lines.append("➖ 策略3无明显信号。")

    # 策略4：风控
    if indicators['rsi']['suggestion'] == "卖出" and indicators['adx']['suggestion'] == "买入" and indicators['atr']['suggestion'] != "卖出":
        report_lines.append("⚠️ 策略4【风险预警】：强趋势+超买+波动提升，需警惕回调风险。")
    else:
        report_lines.append("➖ 策略4未触发风险预警。")

    return "\n".join(report_lines)

def export_analysis_to_markdown(all_results, output_path):
    # 创建 Markdown 文件并写入内容
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入报告标题
        f.write("# 股票分析报告\n\n")

        # 遍历每个股票的分析结果
        for result in all_results:
            stock_code = result['ticker']
            stock_name = result['ticker_name']
            analysis = result['analysis']

            final_decision = analysis['final_decision']
            reasons = "\n".join(analysis['reasons'])
            indicators = analysis['indicators']

            # 写入股票的基本信息
            f.write(f"## {stock_name} ({stock_code})\n\n")
            f.write(f"### 综合建议：{final_decision}\n\n")
            f.write(f"### 分析理由：\n{reasons}\n\n")

            # 写入每个指标的详细建议
            f.write(f"### 各指标建议：\n")
            for indicator_name, indicator_data in indicators.items():
                suggestion = indicator_data['suggestion']
                detailed_suggestion = indicator_data['detailed_suggestion']

                f.write(f"#### {indicator_name.upper()}：{suggestion}\n")
                f.write(f"{detailed_suggestion}\n\n")

            # 添加分隔线，方便区分每支股票的报告
            f.write("\n---\n\n")

def analyze(stock, stock_data, indicator_weights):
    # 检查 stock_data 是否为空或缺少必要字段
    required_fields = ['close']

    # 检查 stock_data 是否为 None 或为空，或者缺少必要的字段
    if stock_data is None or stock_data.empty or not all(field in stock_data.columns for field in required_fields):
        print(f"\n【错误】：没有有效的股票数据或缺少必要的字段")
        return {"final_decision": "没有股票数据", "reasons": [], "indicators": {}}


    # 如果数据有效，开始分析
    print(f"\n==============================")
    print(f"正在分析股票: {stock.ticker} - {stock.ticker_name}")

    # 计算技术指标
    indicators = calculate_indicators(stock_data)

    # 检测市场类型
    market_type = detect_market_type(stock_data)

    # 得到最终建议和理由
    final_decision, reasons = final_suggestion(indicators, market_type, indicator_weights)

    # 返回结构化数据
    return {
        "final_decision": final_decision,
        "reasons": reasons,
        "indicators": indicators
    }
# 批量分析股票并生成报告
def batch_analysis_stocks_report(stocks, start_date, end_date):

    analysis_results = batch_analysis_stocks(stocks, start_date, end_date)

    # 所有分析结束后，生成 Markdown 报告
    export_analysis_to_markdown(analysis_results, output_path="../report/分析报告.md")

# 批量分析股票
def batch_analysis_stocks(stocks, start_date, end_date):
    # 初始化存储分析结果的列表
    analysis_results = []

    # 遍历每个股票
    for ticker in stocks:
        # 使用 ticker 的 symbol 和 name 创建 StockAnalysis 对象
        stock = StockAnalysis(ticker['symbol'], ticker['name'], start_date, end_date)

        # 获取股票数据
        stock_data = stock.data_fetcher.fetch_data()

        # 执行分析函数并获取分析结果
        analyze_result = analyze(stock, stock_data, indicator_weights)

        # 将结果存储到列表中
        analysis_results.append({
            "ticker": stock.ticker,
            "ticker_name": stock.ticker_name,
            "analysis": analyze_result
        })

        return analysis_results

def export_analysis_to_console(all_results):
    # 遍历每个股票的分析结果
    for result in all_results:
        stock_code = result['ticker']
        stock_name = result['ticker_name']
        analysis = result['analysis']

        final_decision = analysis['final_decision']
        reasons = "\n".join(analysis['reasons'])
        indicators = analysis['indicators']

        # 打印股票的基本信息
        print(f"### {stock_name} ({stock_code})\n")

        # 打印综合建议
        print(f"#### 综合建议：{final_decision}\n")

        # 打印分析理由
        print(f"#### 分析理由：")
        print(reasons + "\n")

        # 打印每个指标的详细建议
        print(f"#### 各指标建议：")
        for indicator_name, indicator_data in indicators.items():
            suggestion = indicator_data['suggestion']
            detailed_suggestion = indicator_data['detailed_suggestion']

            print(f"##### {indicator_name.upper()}：{suggestion}")
            print(f"{detailed_suggestion}\n")

        # 打印分隔符，区分每支股票的报告
        print("\n" + "-"*50 + "\n")

# 批量分析股票并打印到控制台
def batch_analysis_stocks_console(stocks_infos,start_date,end_date):
    analysis_results = batch_analysis_stocks(stocks_infos, start_date, end_date)
    export_analysis_to_console(analysis_results)

def from_json(json_data):
    json_data = '''{"data":{"pid":1,"category":1,"stocks":[{"symbol":"SH600054","name":"黄山旅游","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ000524","name":"岭南控股","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ000796","name":"凯撒旅业","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ000888","name":"峨眉山A","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ000978","name":"桂林旅游","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ002033","name":"丽江股份","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ002059","name":"云南旅游","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ002159","name":"三特索道","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ002707","name":"众信旅游","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ300144","name":"宋城演艺","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ000430","name":"张家界","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SH900942","name":"黄山B股","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SH600138","name":"中青旅","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SH600576","name":"祥源文旅","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SH600593","name":"大连圣亚","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SH600706","name":"曲江文旅","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SH600749","name":"西藏旅游","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SH603099","name":"长白山","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SH603136","name":"天目湖","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SH603199","name":"九华旅游","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SH900929","name":"锦旅B股","type":11,"remark":"","exchange":"SH","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"},{"symbol":"SZ300859","name":"西域旅游","type":11,"remark":"","exchange":"SZ","created":1744205721749,"watched":1744205721749,"category":1,"marketplace":"CN"}]},"error_code":0,"error_description":""}'''
    # 将JSON数据解析为Python字典
    data = json.loads(json_data)

    # 提取股票信息
    stocks = data['data']['stocks']

    # 将股票代码和名称放入stocks列表中
    stocks_info = [
        {
            'symbol': f"{stock['symbol'][0:2].lower()}.{stock['symbol'][2:]}" if stock['symbol'][0:2] in ['SH', 'SZ'] else stock['symbol'],
            'name': stock['name']
        }
        for stock in stocks
    ]

    return stocks_info

if __name__ == '__main__':
    # 设定结束日期为当前日期
    end_date = '2025-04-10'

    # 计算开始日期，设为一年之前
    start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")

    # 将字符串转换为Python对象
    stocks_infos = """[{'symbol':'sh.600570','name':'恒生电子'}]"""
    stocks_infos = ast.literal_eval(stocks_infos)  # 安全地将字符串转换为list

    batch_analysis_stocks_console(stocks_infos,start_date,end_date)
