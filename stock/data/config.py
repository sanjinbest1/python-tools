# ================================
# 股票技术指标配置（含详细说明）
# ================================

# 📈 Stochastic RSI 配置（随机相对强弱指标）
STOCHASTIC_RSI = {
    'K_PERIOD': 21,  # %K 周期。控制 RSI 的取样范围。越大越平稳，信号更可靠但更滞后。
    'D_PERIOD': 5,   # %D 平滑周期，对%K进行移动平均，生成更平滑的信号。
    'SMOOTH_K': 5    # 对原始%K值进行额外平滑处理，降低波动性噪音。
    # ▶️ 作用：结合 RSI 与 Stochastic，评估 RSI 在其自身范围内的动量变化，更敏感地识别超买/超卖。
    # 🔍 反映：值接近 1 表示 RSI 接近历史高位（超买），值接近 0 表示 RSI 接近低位（超卖）。
    # 💡 使用建议：
    #   - 适合短线波段操作与震荡市反转策略。
    #   - 可配合布林带或趋势指标过滤信号，避免逆势交易。
}

# 📊 ADX 配置（平均趋向指数）
ADX_CONFIG = {
    "PERIOD": 14,
    "WEAK_TREND_THRESHOLD": 25,
    "MEDIUM_TREND_THRESHOLD": 40,
    "STRONG_TREND_THRESHOLD": 50
    # ▶️ 作用：衡量趋势强度（不分方向），用来识别震荡期与趋势期。
    # 🔍 反映：
    #   - ADX < 25：市场可能处于横盘震荡，趋势信号可靠性较低。
    #   - ADX > 40：市场进入趋势阶段，趋势策略更有效。
    # 💡 使用建议：
    #   - ADX 高于 25 时，优先采用趋势类指标如 MACD、均线系统。
    #   - ADX 低于 25 时，可转向布林带、RSI 等震荡型策略。
}

# 📉 ATR 配置（平均真实波幅）
ATR_CONFIG = {
    "PERIOD": 21,
    "RECENT_WINDOW": 14
    # ▶️ 作用：度量价格波动幅度，用于识别市场活跃程度或设置动态止损。
    # 🔍 反映：
    #   - ATR 上升：波动加剧，可能预示行情启动或剧烈波动来临。
    #   - ATR 下降：市场平稳，适合横盘震荡策略。
    # 💡 使用建议：
    #   - 配合布林带、Keltner 可用于突破判断。
    #   - 设置止损可使用“当前ATR × 系数”方式动态调整。
}

# 🧭 MACD 配置（指数平滑异同移动平均线）
MACD_CONFIG = {
    'fast_period': 10,
    'slow_period': 20,
    'signal_period': 9
    # ▶️ 作用：通过两条 EMA 差值判断价格趋势及其变化速率。
    # 🔍 反映：
    #   - 金叉（MACD线上穿信号线）：趋势可能向上。
    #   - 死叉（MACD线下穿信号线）：可能转为下跌。
    #   - 柱状图放大/缩小：反映动能增强/减弱。
    # 💡 使用建议：
    #   - 趋势市中效果最佳，震荡市中容易产生误导。
    #   - 搭配 ADX 判断是否适合启用趋势策略。
}

# 💪 RSI 配置（相对强弱指标）
RSI_CONFIG = {
    "default_window": 14,
    "window_list": [6, 14, 21],
    "overbought": 80,
    "oversold": 20
    # ▶️ 作用：衡量近期上涨与下跌幅度比例，识别超买/超卖状态。
    # 🔍 反映：
    #   - RSI > 80：市场可能过热，短期顶部风险增加。
    #   - RSI < 20：市场可能超卖，反弹概率提高。
    # 💡 使用建议：
    #   - 不宜单独作为交易依据，建议结合价格形态、趋势确认。
    #   - 多周期 RSI（如 6,14,21）结合可用于动量背离策略。
}

# 📎 Bollinger Band 配置（布林带）
BOLLINGER_CONFIG = {
    "WINDOW": 20,
    "NUM_STD": 2.5
    # ▶️ 作用：构建价格的“正常波动通道”，用于识别突破或极端行为。
    # 🔍 反映：
    #   - 突破上轨：可能为强势上涨或超买。
    #   - 突破下轨：可能为恐慌性下跌或超卖。
    # 💡 使用建议：
    #   - 通常价格会回归中轨，适合震荡市高抛低吸。
    #   - 配合 OBV/VWAP 筛选“假突破”信号。
}

# 🔔 Keltner Channel 配置（凯尔特通道）
KELTNER_CONFIG = {
    "PERIOD": 20,
    "MULTIPLIER": 2.5
    # ▶️ 作用：类似布林带，使用EMA和ATR构建波动通道，判断趋势与突破。
    # 🔍 反映：
    #   - 价格持续运行在上轨以上：强势趋势。
    #   - 跌破下轨：趋势反转或急跌。
    # 💡 使用建议：
    #   - 与布林带交叉使用，识别共振突破。
    #   - 多用于趋势跟随策略中作为入场/加仓判断。
}

# 📦 OBV 配置（能量潮指标）
OBV_CONFIG = {
    "obv_initial_value": 1000,
    "obv_threshold_positive": 0.3,
    "obv_threshold_negative": -0.3
    # ▶️ 作用：通过成交量与价格关系推测资金流入流出情况。
    # 🔍 反映：
    #   - OBV 持续上升：多头量能增强。
    #   - OBV 下降：市场做空能量释放。
    # 💡 使用建议：
    #   - 适合与趋势类指标（如MACD）组合确认有效性。
    #   - 突破信号需有 OBV 支持才更可靠。
}

# 🧮 VWAP 配置（成交量加权平均价）
VWAP_CONFIG = {
    "buy_threshold": 1.5,
    "sell_threshold": -1.5
    # ▶️ 作用：衡量当前价格相对市场平均成本的位置，常用于判断交易性价比。
    # 🔍 反映：
    #   - 当前价高于VWAP +1.5%：强势运行，主力可能持续推高。
    #   - 当前价低于VWAP -1.5%：资金抛压明显，注意风险。
    # 💡 使用建议：
    #   - 日内交易/机构进出场监控非常有效。
    #   - 配合价格行为与趋势指标过滤虚假信号。
}
