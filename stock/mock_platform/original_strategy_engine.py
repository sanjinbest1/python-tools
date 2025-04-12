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
    'rsi': 0.2,
    'macd': 0.15,
    'bollinger': 0.1,
    'adx': 0.2,
    'atr': 0.05,
    'obv': 0.1,
    'vwap': 0.1,
    'stochastic_rsi': 0.05,
    'keltner': 0.05
}

# ==== Step 1: 指标计算 ====
def calculate_indicators_raw_and_suggestions(stock_data):
    rsi_raw = calculate_rsi_for_multiple_windows(stock_data)
    macd_line, signal_line, macd_hist = calculate_macd(stock_data['close'])
    boll_raw = calculate_bollinger_bands(stock_data)
    boll_signal = generate_bollinger_signals(boll_raw)
    obv_raw = calculate_obv(stock_data)
    vwap_raw = calculate_vwap(stock_data)
    stoch_rsi_raw = calculate_stochastic_rsi(stock_data)
    adx_raw = calculate_adx_safe(stock_data)
    atr_raw = calculate_atr(stock_data)
    keltner_raw = calculate_keltner_channel(stock_data)

    return {
        'rsi': {
            'raw': rsi_raw,
            'suggestion': generate_operation_suggestion(rsi_raw)['suggestion'],
            'explanation': generate_operation_suggestion(rsi_raw)['detailed_suggestion']
        },
        'macd': {
            'raw': {'macd': macd_line, 'signal': signal_line, 'hist': macd_hist},
            'suggestion': generate_macd_signal(macd_line, signal_line, macd_hist)['suggestion'],
            'explanation': generate_macd_signal(macd_line, signal_line, macd_hist)['detailed_suggestion']
        },
        'bollinger': {
            'raw': boll_raw,
            'suggestion': generate_bollinger_operations(boll_signal)['suggestion'],
            'explanation': generate_bollinger_operations(boll_signal)['detailed_suggestion']
        },
        'obv': {
            'raw': obv_raw,
            'suggestion': generate_obv_operation_suggestion(obv_raw, stock_data)['suggestion'],
            'explanation': generate_obv_operation_suggestion(obv_raw, stock_data)['detailed_suggestion']
        },
        'vwap': {
            'raw': vwap_raw,
            'suggestion': generate_vwap_operation_suggestion(stock_data, vwap_raw)['suggestion'],
            'explanation': generate_vwap_operation_suggestion(stock_data, vwap_raw)['detailed_suggestion']
        },
        'stochastic_rsi': {
            'raw': stoch_rsi_raw,
            'suggestion': generate_stochastic_rsi_operation_suggestion(stoch_rsi_raw)['suggestion'],
            'explanation': generate_stochastic_rsi_operation_suggestion(stoch_rsi_raw)['detailed_suggestion']
        },
        'adx': {
            'raw': adx_raw,
            'suggestion': generate_adx_operation_suggestion(adx_raw)['suggestion'],
            'explanation': generate_adx_operation_suggestion(adx_raw)['detailed_suggestion']
        },
        'atr': {
            'raw': atr_raw,
            'suggestion': generate_atr_operation_suggestion(atr_raw)['suggestion'],
            'explanation': generate_atr_operation_suggestion(atr_raw)['detailed_suggestion']
        },
        'keltner': {
            'raw': keltner_raw,
            'suggestion': generate_keltner_channel_operation_suggestion(keltner_raw)['suggestion'],
            'explanation': generate_keltner_channel_operation_suggestion(keltner_raw)['detailed_suggestion']
        }
    }

def score_indicators_from_raw(indicators_raw, market_type="trend"):
    """
    将每个指标的原始值映射为 [0,1] 区间的评分，用于加权融合。
    可以根据市场类型（震荡或趋势）动态调整权重。
    """
    scores = {}
    current_close = indicators_raw['bollinger']['close'].iloc[-1]  # 获取最新的收盘价

    # 1. RSI评分（多窗口期）
    rsi_values = indicators_raw.get('rsi')
    if isinstance(rsi_values, dict):
        # 选择多个窗口期的平均 RSI 或选择最佳窗口期的 RSI
        avg_rsi = np.mean(list(rsi_values.values()))  # 计算多个窗口期 RSI 的平均值
        rsi_value = avg_rsi
    else:
        rsi_value = rsi_values

    if rsi_value is not None and not pd.isna(rsi_value):  # 处理 NaN
        if rsi_value < 30:
            scores['rsi'] = min(1, (30 - rsi_value) / 30)  # 越低越接近买入
        elif rsi_value > 70:
            scores['rsi'] = max(0, 1 - (rsi_value - 70) / 30)  # 越高越偏卖出
        else:
            scores['rsi'] = 0.5  # 中性区
    else:
        scores['rsi'] = 0.5  # 如果没有有效的 RSI 数据，给一个默认值

    # 2. MACD评分（根据柱状图）
    macd_hist = indicators_raw.get('macd', {}).get('hist', None)
    if macd_hist is not None and not macd_hist.empty:
        recent_hist = macd_hist.iloc[-1]
        scores['macd'] = 1 / (1 + np.exp(-recent_hist * 10))  # Sigmoid 映射

    # 3. Bollinger评分（接近下轨 = 买入机会）
    boll = indicators_raw.get('bollinger')
    if boll is not None and not boll.empty:
        close = boll['close'].iloc[-1]
        lower = boll['low'].iloc[-1]
        upper = boll['high'].iloc[-1]
        width = upper - lower
        if width > 0:
            pos = (close - lower) / width  # 0 接近下轨，1 接近上轨
            scores['bollinger'] = 1 - pos  # 越接近下轨越接近买入

    # 4. OBV评分（斜率为正 → 买入）
    obv = indicators_raw.get('obv')
    if obv is not None and not obv.empty and len(obv) >= 5:
        slope = np.polyfit(range(5), obv[-5:], 1)[0]
        scores['obv'] = 1 / (1 + np.exp(-slope * 10))

    # VWAP评分（价格低于VWAP → 低估）
    vwap = indicators_raw.get('vwap')
    if vwap is not None and not vwap.empty and not vwap.isna().any():  # 检查 vwap 是否为空，且没有 NaN
        diff_ratio = (current_close - vwap) / vwap
        scores['vwap'] = 1 / (1 + np.exp(diff_ratio * 20))

    # Stochastic RSI（0接近超卖，1超买）
    stoch = indicators_raw.get('stochastic_rsi')
    if isinstance(stoch, pd.Series) and not stoch.empty and not stoch.isna().any():  # 确保是Series且无NaN值
        scores['stochastic_rsi'] = 1 - stoch.iloc[-1]  # 越低越好

    # ADX评分（趋势强 → 给高分）
    adx = indicators_raw.get('adx')
    if adx is not None and not adx.empty:
        adx_value = adx.iloc[-1]  # 获取最新的 ADX 值
        scores['adx'] = min(1.0, adx_value / 50)  # 50作为强趋势上限

    # ATR评分（波动率，风险指标 → 越低越好）
    atr = indicators_raw.get('atr')
    if atr is not None and not atr.empty:
        atr_value = atr.iloc[-1]  # 获取最新的 ATR 值
        ratio = atr_value / current_close  # 当前ATR与收盘价比值
        scores['atr'] = max(0, 1 - ratio * 5)  # ATR过高风险高，分数低

    # 9. Keltner评分（接近下轨买入机会）
    kel = indicators_raw.get('keltner')
    if kel is not None and not kel.empty:
        pos = (current_close - kel['low'].iloc[-1]) / (kel['high'].iloc[-1] - kel['low'].iloc[-1])
        scores['keltner'] = 1 - pos

    # 根据市场类型调整权重
    if market_type == "trend":
        # 在趋势市场中，较长窗口期的 RSI 更加重要
        # 增加 RSI 和 ADX 的权重
        scores['rsi'] *= 1.2  # 提高 RSI 的权重
        scores['adx'] *= 1.5  # 提高 ADX 的权重
    elif market_type == "range":
        # 在震荡市场中，较短窗口期的 RSI 更加重要
        # 增加布林带、RSI（短期）的权重
        scores['rsi'] *= 0.8  # 减少 RSI 权重
        scores['bollinger'] *= 1.5  # 提高布林带的权重

    # 确保评分在 [0, 1] 范围内
    scores = {key: score.clip(0, 1) if isinstance(score, pd.Series) else min(max(score, 0), 1)
              for key, score in scores.items()}

    return scores

def generate_operation_suggestion_from_scores(indicator_scores, indicator_weights):
    """
    加权融合评分，生成综合建议，并提供不同持仓情况下的具体操作建议。
    """
    weighted_sum = 0
    total_weight = 0

    for name, score in indicator_scores.items():
        weight = indicator_weights.get(name, 0)

        # 如果 score 是字典，输出警告并尝试提取数值
        if isinstance(score, dict):
            print(f"Warning: Score for {name} is a dictionary. Attempting to extract a value.")
            score = score.get('value', 0)
            print(f"Extracted score for {name}: {score}")

        # 确保 score 是数值类型
        if isinstance(score, (int, float)):
            weighted_sum += score * weight
            total_weight += weight
        else:
            print(f"Error: Indicator '{name}' score is not a valid number: {score}")

    # 计算最终分数
    final_score = weighted_sum / total_weight if total_weight > 0 else 0.5

    # 建议映射规则
    if final_score >= 0.8:
        suggestion = '强烈买入'
    elif final_score >= 0.65:
        suggestion = '买入'
    elif final_score >= 0.5:
        suggestion = '谨慎买入'
    elif final_score >= 0.35:
        suggestion = '观望'
    elif final_score >= 0.2:
        suggestion = '卖出'
    else:
        suggestion = '强烈卖出'

    # 仓位建议（根据评分生成不同仓位的建议）
    if suggestion == "强烈买入":
        operation_detail = "建议大幅增仓，仓位可接近 100%。"
        stop_loss = "建议设置止损位于当前价格下方 5% 左右。"
        take_profit = "建议设置止盈位于当前价格上方 15% 左右。"
    elif suggestion == "买入":
        operation_detail = "可以适度增仓，建议将当前仓位提升至 70%。"
        stop_loss = "建议设置止损位于当前价格下方 5% 左右。"
        take_profit = "建议设置止盈位于当前价格上方 10% 左右。"
    elif suggestion == "谨慎买入":
        operation_detail = "建议适度增仓，仓位控制在 30% 左右。"
        stop_loss = "建议设置止损位于当前价格下方 5% 左右。"
        take_profit = "建议设置止盈位于当前价格上方 8% 左右。"
    elif suggestion == "观望":
        operation_detail = "当前无明确的操作建议，保持现有仓位。"
        stop_loss = "无止损建议，维持现有仓位。"
        take_profit = "无止盈建议，维持现有仓位。"
    elif suggestion == "卖出":
        operation_detail = "建议逐步减仓，考虑将仓位减至 20% 以下。"
        stop_loss = "建议设置止损位于当前价格上方 5% 左右。"
        take_profit = "建议设置止盈位于当前价格下方 10% 左右。"
    else:  # 强烈卖出
        operation_detail = "建议迅速减仓，仓位控制在 10% 以下。"
        stop_loss = "建议设置止损位于当前价格上方 5% 左右。"
        take_profit = "建议设置止盈位于当前价格下方 15% 左右。"

    return {
        'final_score': round(final_score, 3),
        'suggestion': suggestion,
        'reason': f"融合评分为 {round(final_score, 3)}，建议为 {suggestion}",
        'operation_detail': operation_detail,
        'stop_loss': stop_loss,
        'take_profit': take_profit
    }

def export_analysis_to_markdown(all_results, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 股票分析报告\n\n")

        for result in all_results:
            stock_code = result['ticker']
            stock_name = result['ticker_name']
            final_suggestion = result.get('final_suggestion', '无')
            final_score = result.get('final_score', '无评分')
            reason = result.get('reason', '')  # 获取综合建议说明
            operation_detail = result.get('operation_detail', '')  # 获取操作建议
            stop_loss = result.get('stop_loss', '')  # 获取止损建议
            take_profit = result.get('take_profit', '')  # 获取止盈建议

            # 写入股票信息与综合建议
            f.write(f"## {stock_name} ({stock_code})\n\n")
            f.write(f"### 综合建议：{final_suggestion}（评分：{round(final_score, 2)}）\n\n")
            f.write(f"### 综合建议说明：{reason}\n\n")
            f.write(f"### 操作建议：{operation_detail}\n\n")
            f.write(f"### 止损建议：{stop_loss}\n\n")
            f.write(f"### 止盈建议：{take_profit}\n\n")

            f.write("### 各指标建议与解释：\n\n")

            # 提取所有 *_suggestion 和 *_explanation 项
            for key in sorted(result.keys()):
                if key.endswith("_suggestion"):
                    indicator = key.replace("_suggestion", "").upper()
                    suggestion = result[key]
                    explanation = result.get(f"{key.replace('_suggestion', '_explanation')}", "无解释")

                    f.write(f"#### {indicator}\n")
                    f.write(f"- 建议：{suggestion}\n")
                    f.write(f"- 说明：{explanation}\n\n")

            f.write("---\n\n")


def analyze(stock, stock_data):
    # 检查 stock_data 是否为空或缺少必要字段
    required_fields = ['close']

    # 检查 stock_data 是否为 None 或为空，或者缺少必要的字段
    if stock_data is None or stock_data.empty or not all(field in stock_data.columns for field in required_fields):
        print(f"\n【错误】：没有有效的股票数据或缺少必要的字段")
        return {"final_decision": "没有股票数据", "reasons": [], "indicators": {}}


    # 如果数据有效，开始分析
    print(f"\n==============================")
    print(f"正在分析股票: {stock.ticker} - {stock.ticker_name}")

    indicators = calculate_indicators_raw_and_suggestions(stock_data)
    market_type = calculate_market_type_from_indicators(indicators,stock_data)
    dynamic_indicator_weights = adjust_weights_for_market(market_type)  # 动态调整权重

    # 提取原始值、解释和建议
    raw_values = {key: indicators[key]['raw'] for key in indicators}
    explanations = {key: indicators[key].get('explanation', '无解释') for key in indicators}
    suggestions = {key: indicators[key].get('suggestion', '无建议') for key in indicators}

    indicator_scores = score_indicators_from_raw(raw_values)
    operation_suggestion = generate_operation_suggestion_from_scores(indicator_scores, dynamic_indicator_weights)

    # 返回操作建议和其他相关数据
    final_score = operation_suggestion['final_score']
    suggestion = operation_suggestion['suggestion']
    reason = operation_suggestion['reason']
    operation_detail = operation_suggestion.get('operation_detail', '无')
    stop_loss = operation_suggestion.get('stop_loss', '无')
    take_profit = operation_suggestion.get('take_profit', '无')

    # 组织分析结果
    analysis_result = {
        'ticker': stock.ticker,
        'ticker_name': stock.ticker_name,
        'final_score': final_score,
        'final_suggestion': suggestion,
        'reason': reason,
        'operation_detail': operation_detail,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'raw_values': raw_values,  # 添加原始值
        'explanations': explanations,  # 添加解释
        'suggestions': suggestions  # 添加建议
    }

    return analysis_result

def adjust_weights_for_market(market_type="trend"):
    """
    根据市场类型动态调整指标权重。
    :param market_type: str，市场类型，"trend" 或 "sideways" 或 "neutral"。
    :return: dict，调整后的权重字典。
    """
    adjusted_weights = indicator_weights.copy()

    if market_type == "trend":
        # 提升趋势指标的权重，降低震荡相关指标的权重
        adjusted_weights['adx'] *= 1.5
        adjusted_weights['rsi'] *= 1.2
        adjusted_weights['bollinger'] *= 0.8
        adjusted_weights['obv'] *= 1.1

    elif market_type == "sideways":
        # 提升震荡市场相关指标的权重
        adjusted_weights['rsi'] *= 1.3
        adjusted_weights['bollinger'] *= 1.5
        adjusted_weights['obv'] *= 1.1
        adjusted_weights['adx'] *= 0.8

    # 中性市场保持默认权重
    return adjusted_weights


def calculate_market_type_from_indicators(indicators, stock_data):
    """
    基于 `calculate_indicators_raw_and_suggestions` 函数的返回值来判断市场类型。
    - 如果 `ADX` 强，说明是趋势市场。
    - 如果 `RSI` 在 30 和 70 之间，且 `Bollinger Bands` 上下轨之间震荡，说明是震荡市场。
    - 否则判断为中性市场。
    """
    # 获取指标
    adx_value = indicators.get('adx', {}).get('raw', None)
    rsi_values = indicators.get('rsi', {}).get('raw', None)  # rsi 是一个序列
    bollinger = indicators.get('bollinger', {}).get('raw', None)

    # 如果缺少任何一个必要的指标，返回无法识别
    if adx_value is None or rsi_values is None or bollinger is None:
        return "unknown"  # 无法判断

    # 如果 adx_value 是 Series，获取最后一个值
    if isinstance(adx_value, pd.Series):
        adx_value = adx_value.iloc[-1]  # 获取最后一个值

    # 判断趋势市场（ADX > 25 强趋势）
    if adx_value > 25:
        return "trend"

    # 判断震荡市场（RSI 在 30 和 70 之间，且布林带内震荡）
    if isinstance(rsi_values, pd.Series):
        latest_rsi = rsi_values.iloc[-1]  # 获取 RSI 序列的最新值
    else:
        latest_rsi = rsi_values  # 如果 rsi_values 不是 Series，直接使用它

    # 判断 RSI 是否在 30 和 70 之间，且布林带上下轨之间震荡
    if 30 < latest_rsi < 70:
        # 检查股票价格是否在布林带的上下轨之间
        latest_close = stock_data['close'].iloc[-1]
        if bollinger['lower'] < latest_close < bollinger['upper']:
            return "sideways"

    # 默认判断为中性市场
    return "neutral"





# 批量分析股票并生成报告
def batch_analysis_stocks_report(stocks, start_date, end_date):

    analysis_results = batch_analysis_stocks(stocks, start_date, end_date)

    # 所有分析结束后，生成 Markdown 报告
    export_analysis_to_markdown(analysis_results, output_path="../report/分析报告.md")

# 批量分析股票
def batch_analysis_stocks(stocks, start_date, end_date):
    analysis_results = []

    for ticker in stocks:
        stock = StockAnalysis(ticker['symbol'], ticker['name'], start_date, end_date)
        stock_data = stock.data_fetcher.fetch_data()

        # 分析股票数据
        analyze_result = analyze(stock, stock_data)

        # 构建股票分析结果
        result_entry = {
            "ticker": stock.ticker,
            "ticker_name": stock.ticker_name,
            "final_suggestion": analyze_result["final_suggestion"],
            "final_score": round(analyze_result["final_score"], 2),
            "reason": analyze_result["reason"],
            "operation_detail": analyze_result["operation_detail"],
            "stop_loss": analyze_result["stop_loss"],
            "take_profit": analyze_result["take_profit"],
        }

        # 将各指标建议和解释合并进入结果中
        for indicator_name, suggestion in analyze_result["suggestions"].items():
            result_entry[f"{indicator_name}_suggestion"] = suggestion

        for indicator_name, explanation in analyze_result["explanations"].items():
            result_entry[f"{indicator_name}_explanation"] = explanation

        # 将结果添加到返回列表中
        analysis_results.append(result_entry)

    return analysis_results



def from_json():
    json_data = '''{
  "data": {
    "pid": 2,
    "category": 1,
    "stocks": [
      {
        "symbol": "SH603236",
        "name": "移远通信",
        "type": 11,
        "remark": "",
        "exchange": "SH",
        "created": 1744248566504,
        "watched": 1744248566504,
        "category": 1,
        "marketplace": "CN"
      },
      {
        "symbol": "SZ300377",
        "name": "赢时胜",
        "type": 11,
        "remark": "",
        "exchange": "SZ",
        "created": 1744248540608,
        "watched": 1744248540608,
        "category": 1,
        "marketplace": "CN"
      },
      {
        "symbol": "00241",
        "name": "阿里健康",
        "type": 30,
        "remark": "",
        "exchange": "HK",
        "created": 1744248529498,
        "watched": 1744248529498,
        "category": 1,
        "marketplace": "HK"
      },
      {
        "symbol": "01810",
        "name": "小米集团-W",
        "type": 30,
        "remark": "",
        "exchange": "HK",
        "created": 1744248524651,
        "watched": 1744248524651,
        "category": 1,
        "marketplace": "HK"
      },
      {
        "symbol": "SZ002657",
        "name": "中科金财",
        "type": 11,
        "remark": "",
        "exchange": "SZ",
        "created": 1744248519559,
        "watched": 1744248519559,
        "category": 1,
        "marketplace": "CN"
      },
      {
        "symbol": "SH600446",
        "name": "金证股份",
        "type": 11,
        "remark": "",
        "exchange": "SH",
        "created": 1744248514335,
        "watched": 1744248514335,
        "category": 1,
        "marketplace": "CN"
      },
      {
        "symbol": "SH600570",
        "name": "恒生电子",
        "type": 11,
        "remark": "",
        "exchange": "SH",
        "created": 1744248509501,
        "watched": 1744248509501,
        "category": 1,
        "marketplace": "CN"
      }
    ]
  },
  "error_code": 0,
  "error_description": ""
}'''
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
    end_date = '2025-04-12'

    # 计算开始日期，设为一年之前
    start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")

    # 将字符串转换为Python对象
    # stocks_infos = """[{'symbol':'sh.600570','name':'恒生电子'}]"""
    # stocks_infos = ast.literal_eval(stocks_infos)  # 安全地将字符串转换为list

    stocks_infos = from_json()

    batch_analysis_stocks_report(stocks_infos,start_date,end_date)
