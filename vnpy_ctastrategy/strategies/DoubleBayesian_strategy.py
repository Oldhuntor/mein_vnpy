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
from scipy.stats import binom
import pandas as pd
class DoubleBayesianStrategy(CtaTemplate):
    author = "Xuanhao"

    prior = 0
    posterior = 0
    long_trend_window_size = 5
    short_trend_window_size = 5
    long_trend_period = 60
    short_trend_period = 5
    fix_size = 1
    buy_threshold = 0.55
    sell_threshold = 0.45
    parameters = ["prior", "long_trend_window_size","short_trend_window_size","long_trend_period", "short_trend_period" ,"fix_size", "buy_threshold", "sell_threshold"]
    variables = ["bayesian_prob"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg_long = BarGenerator(self.on_bar, self.long_trend_period, self.on_long_bar)
        self.bg_short = BarGenerator(self.on_bar, self.short_trend_period, self.on_short_bar)
        self.am_long = ArrayManager(self.long_trend_window_size)
        self.am_short = ArrayManager(self.short_trend_window_size)
        self.bayesian_stat = []

    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        self.write_log("策略停止")
        self.put_event()

    # def on_tick(self, tick: TickData):
    #     self.bg.update_tick(tick)
    #
    def on_bar(self, bar: BarData):
        self.bg_long.update_bar(bar)
        self.bg_short.update_bar(bar)


    def on_long_bar(self, long_bar: BarData):
        self.am_long.update_bar(long_bar)
        if not self.am_long.inited:
            return
        ups = sum(1 for index in range(self.am_long.size) if self.am_long.close_array[index] > self.am_long.open_array[index])
        # update prior
        self.prior = ups/self.long_trend_window_size

    def on_short_bar(self, short_bar: BarData):
        self.am_short.update_bar(short_bar)
        if not self.am_short.inited:
            return

        if self.prior == 0:
            return

        ups = sum(1 for index in range(self.am_short.size) if self.am_short.close_array[index] > self.am_short.open_array[index])
        likelihood = self.compute_likelihood(ups)
        if likelihood == 0:
            return

        p_D = self.compute_normalizing_constant(ups)
        self.posterior = likelihood * self.prior / p_D
        msg = f"posterior: {self.posterior}, prior: {self.prior}, likelihood: {likelihood}，compute_normalizing_constant:{p_D}"
        print(msg)
        self.bayesian_stat.append(msg)


        if self.posterior >= self.buy_threshold and self.pos == 0:
            self.buy(short_bar.close_price, self.fix_size)
            # print(f"buy {self.fix_size} at price {short_bar.close_price} on {short_bar.datetime}")

        elif self.posterior <= self.sell_threshold and self.pos !=0:
            self.sell(short_bar.close_price, self.fix_size)
            # print(f"sell {self.fix_size} at price {short_bar.close_price} on {short_bar.datetime}")


    def compute_likelihood(self, ups):
        likelihood:float = binom.pmf(ups, self.am_short.size, self.prior)
        return likelihood

    def compute_normalizing_constant(self, ups):
        """
        Compute the normalizing constant p(D) using a sequence of prior values.
        """
        prior_values = np.linspace(0, 1, self.long_trend_window_size)
        p_D = sum(binom.pmf(ups, self.am_short.size, prior) * self.prior for prior in prior_values)
        return p_D

    def on_order(self, order):
        pass

    def on_trade(self, trade):
        pass

    def on_stop_order(self, stop_order):
        pass
