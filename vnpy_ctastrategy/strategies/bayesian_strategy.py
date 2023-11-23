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
import numpy as np
class BayesianIndicatorStrategy(CtaTemplate):
    author = "Xuanhao"

    bayesian_window = 20
    prior_probability_up = 0.5
    probability_earnings_beat = 0.7
    probability_up_given_earnings_beat = 0.8
    fix_size = 1
    buy_threshold = 0.55
    sell_threshold = 0.45
    parameters = ["bayesian_window", "prior_probability_up", "probability_earnings_beat", "probability_up_given_earnings_beat","fix_size", "buy_threshold", "sell_threshold"]
    variables = ["bayesian_prob"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bayesian_prob = 0
        self.klines = []
        self.bg = BarGenerator(self.on_bar, self.bayesian_window, self.on_window_bar)
        self.am = ArrayManager(self.bayesian_window*2)

    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        self.write_log("策略停止")
        self.put_event()

    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        self.bg.update_bar(bar)

    def on_window_bar(self, window_bar: BarData):
        self.am.update_bar(window_bar)
        if not self.am.inited:
            return

        self.bayesian_prob = self.calculate_bayesian_prob()

        if self.bayesian_prob == 0:
            return

        if self.bayesian_prob >= self.buy_threshold:
            self.buy(BarData.open_price,volume=self.fix_size)
        elif self.bayesian_prob <= self.sell_threshold:
            self.sell(BarData.open_price,volume=self.fix_size)

        self.put_event()

    def calculate_bayesian_prob(self):
        # Your Bayesian indicator logic here, using self.klines list

        ups = sum(1 for index in range(self.am.size) if self.am.close_array[index] > self.am.open_array[index])  # Count how many times close is greater than open


        likelihood_up = ups / self.bayesian_window

        # Bayesian update
        posterior_probability_up = (self.probability_up_given_earnings_beat * self.prior_probability_up) / self.probability_earnings_beat

        # Adjust posterior based on the likelihood from the klines window
        adjusted_posterior_up = posterior_probability_up * likelihood_up

        return adjusted_posterior_up

    def on_order(self, order):
        pass

    def on_trade(self, trade):
        pass

    def on_stop_order(self, stop_order):
        pass
