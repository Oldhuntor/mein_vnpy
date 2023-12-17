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
from vnpy.trader.object import Interval
from scipy.stats import gamma, poisson

interval_map = {"m": Interval.MINUTE,
                "h": Interval.HOUR,
                "d": Interval.DAILY}

class PoissonGammaStrategy(CtaTemplate):
    author = "Xuanhao"

    prior = 0
    pyramiding = 1
    frequency = 24
    long_trend_window_size = 5
    short_trend_window_size = 5
    long_trend_period = 1 # 1hour 2hour
    short_trend_period = 5 # 5 minutes
    long_trend_interval = "m"
    short_trend_interval = "m"
    fix_size = 1
    buy_threshold = 0.55
    sell_threshold = 0.45
    dual_side = 1
    parameters = ["dual_side", "pyramiding", "long_trend_window_size","short_trend_window_size","long_trend_period", "short_trend_period" ,"fix_size", "buy_threshold", "sell_threshold", "frequency", "long_trend_interval", "short_trend_interval"]
    variables = ["bayesian_prob"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        long_interval = interval_map[self.long_trend_interval]
        short_interval = interval_map[self.short_trend_interval]

        self.bg_long = BarGenerator(self.on_bar, self.long_trend_period, self.on_long_bar, interval=long_interval)
        self.bg_short = BarGenerator(self.on_bar, self.short_trend_period, self.on_short_bar, interval=short_interval)
        self.am_long = ArrayManager(self.long_trend_window_size*self.frequency)
        self.am_short = ArrayManager(self.short_trend_window_size*self.frequency)
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
        poisson_event = []
        for order in range(self.long_trend_window_size):
            ups = sum(1 for index in np.arange((order)*self.frequency, (order+1)*self.frequency, 1) if
                      self.am_long.close_array[index] > self.am_long.open_array[index])
            poisson_event.append(ups)

        mean = np.mean(poisson_event)
        variance = np.var(poisson_event)

        ## MM estimator
        self.alpha_prior = mean ** 2 / variance
        self.beta_prior = mean / variance

        self.priors_inited = True

    def on_short_bar(self, short_bar: BarData):
        self.am_short.update_bar(short_bar)
        if not self.am_short.inited:
            return

        if not self.priors_inited:
            return

        poisson_event = []

        for order in range(self.short_trend_window_size):
            ups = sum(1 for index in np.arange((order) * self.frequency, (order + 1) * self.frequency, 1) if
                      self.am_short.close_array[index] > self.am_short.open_array[index])
            poisson_event.append(ups)

        self.alpha_post = self.alpha_prior + sum(poisson_event)
        self.beta_post = self.beta_prior + self.short_trend_window_size

        # use posterior mean or mode
        self.poster_mean = self.alpha_post/self.beta_post
        self.poster_var = self.alpha_post/(self.beta_post)**2
        self.poster_mode = (self.alpha_post-1)/self.beta_post

        if self.dual_side:
            # both long and short
            if self.poster_mode/self.short_trend_window_size > self.buy_threshold:
                if self.pos >= 0:
                    if abs(self.pos) < self.pyramiding:
                        self.buy(short_bar.close_price, self.fix_size)
                else:
                    self.cover(short_bar.close_price, abs(self.pos))
                    self.buy(short_bar.close_price, self.fix_size)


            if self.poster_mode/self.short_trend_window_size < self.sell_threshold:
                if self.pos <= 0:
                    if abs(self.pos) < self.pyramiding:
                        self.short(short_bar.close_price, self.fix_size)
                else:
                    self.sell(short_bar.close_price, abs(self.pos))
                    self.short(short_bar.close_price, self.fix_size)

        else:
            if self.poster_mode/self.short_trend_window_size > self.buy_threshold:
                if self.pos >= 0 and self.pos < self.pyramiding:
                    self.buy(short_bar.close_price, self.fix_size)

            if self.poster_mode/self.short_trend_window_size < self.sell_threshold:
                if self.pos != 0:
                    self.sell(short_bar.close_price, self.pos)
