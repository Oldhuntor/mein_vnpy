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
from scipy.stats import binom,beta
import pandas as pd

class BayesBetaBinomial(CtaTemplate):
    author = "Xuanhao"

    prior = 0
    pyramiding = 1
    long_trend_window_size = 5
    short_trend_window_size = 5
    long_trend_period = 60
    short_trend_period = 5
    fix_size = 1
    buy_threshold = 0.55
    sell_threshold = 0.45
    dual_side = 1
    parameters = ["dual_side", "pyramiding", "long_trend_window_size","short_trend_window_size","long_trend_period", "short_trend_period" ,"fix_size", "buy_threshold", "sell_threshold"]
    variables = ["bayesian_prob"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg_long = BarGenerator(self.on_bar, self.long_trend_period, self.on_long_bar)
        self.bg_short = BarGenerator(self.on_bar, self.short_trend_period, self.on_short_bar)
        self.am_long = ArrayManager(self.long_trend_window_size)
        self.am_short = ArrayManager(self.short_trend_window_size)
        self.priors_inited = False

    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        self.write_log("策略停止")
        self.put_event()

    def on_bar(self, bar: BarData):
        self.bg_long.update_bar(bar)
        self.bg_short.update_bar(bar)


    def on_long_bar(self, long_bar: BarData):
        self.am_long.update_bar(long_bar)
        if not self.am_long.inited:
            return

        ups = sum(1 for index in range(self.am_long.size) if self.am_long.close_array[index] > self.am_long.open_array[index])
        self.alpha = ups + 1
        self.beta_param = self.am_long.size - ups + 1
        self.priors_inited = True


    def on_short_bar(self, short_bar: BarData):
        self.am_short.update_bar(short_bar)
        if not self.am_short.inited:
            return

        if not self.priors_inited:
            return

        ups = sum(1 for index in range(self.am_short.size) if self.am_short.close_array[index] > self.am_short.open_array[index])
        pred_post = (self.alpha + ups) / (self.alpha + self.beta_param + self.am_short.size)


        random_number = np.random.rand()
        if self.dual_side:
            if random_number < pred_post:

                # both long and short
                if pred_post > self.buy_threshold:
                    if self.pos >= 0:
                        if abs(self.pos) < self.pyramiding:
                            self.buy(short_bar.close_price, self.fix_size)
                    else:
                        self.cover(short_bar.close_price, abs(self.pos))
                        self.buy(short_bar.close_price, self.fix_size)


                if pred_post < self.sell_threshold:
                    if self.pos <= 0:
                        if abs(self.pos) < self.pyramiding:
                            self.short(short_bar.close_price, self.fix_size)
                    else:
                        self.sell(short_bar.close_price, abs(self.pos))
                        self.short(short_bar.close_price, self.fix_size)

        else:
            if pred_post > self.buy_threshold:
                if self.pos >= 0 and self.pos < self.pyramiding:
                    self.buy(short_bar.close_price, self.fix_size)

            if pred_post < self.sell_threshold:
                if self.pos != 0:
                    self.sell(short_bar.close_price, self.pos)




    def on_order(self, order):
        pass

    def on_trade(self, trade):
        pass

    def on_stop_order(self, stop_order):
        pass
