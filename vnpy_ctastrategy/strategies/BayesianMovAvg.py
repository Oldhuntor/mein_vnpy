from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)

class BayesianMaStrategy(CtaTemplate):
    author = "Your Name"

    fast_window = 5
    slow_window = 20
    N = 30
    volatility_factor = 1.0
    parameters = ["fast_window", "slow_window", "N", "volatility_factor"]
    variables = ["ma_trend", "volatility"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, self.N, self.on_N_bars)
        self.am = ArrayManager()

    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        self.write_log("策略停止")
        self.put_event()

    def on_tick(self, tick):
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        fast_ma = self.am.sma(self.fast_window)
        slow_ma = self.am.sma(self.slow_window)
        ma_diff = fast_ma - slow_ma

        volatility = self.am.std(self.N)

        # 更新概率
        prob_upcross = max(min(ma_diff, 1.0), 0.0)  # 简化的概率计算
        adjusted_prob = prob_upcross * (1 + volatility * self.volatility_factor)

        if adjusted_prob > 0.5:
            self.buy(bar.close_price, 1)
        elif adjusted_prob < 0.5:
            self.sell(bar.close_price, 1)


    def on_N_bars(self, bars):
        pass

    def on_order(self, order):
        pass

    def on_trade(self, trade):
        pass

    def on_stop_order(self, stop_order):
        pass
