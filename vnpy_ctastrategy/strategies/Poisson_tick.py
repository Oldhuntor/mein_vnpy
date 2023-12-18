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
                "d": Interval.DAILY,
                "t": Interval.TICK}

from queue import Queue
class PoissonTick(CtaTemplate):
    author = "Xuanhao"

    prior = 0
    pyramiding = 1
    frequency = 24
    long_trend_window_size = 5
    short_trend_window_size = 5
    fix_size = 1
    buy_threshold = 0.55
    sell_threshold = 0.45
    dual_side = 1
    poster_mode = 0
    parameters = ["dual_side", "pyramiding", "long_trend_window_size","short_trend_window_size","fix_size", "buy_threshold", "sell_threshold","frequency"]
    variables = ["poster_mode"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.am_long = Queue(self.long_trend_window_size*self.frequency + 1)
        self.am_short = Queue(self.short_trend_window_size*self.frequency + 1)
        self.priors_inited = False
        self.posterior_inited = False
        self.put_event()


    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        self.write_log("策略停止")
        self.put_event()

    def on_tick(self, tick: TickData) -> None:
        print(tick.last_price)

        if len(self.am_long.queue) < (self.long_trend_window_size*self.frequency + 1):
            self.am_long.put(tick.last_price)
            return

        if len(self.am_short.queue) < (self.short_trend_window_size*self.frequency + 1):
            self.am_short.put(tick.last_price)
            return

        if len(self.am_long.queue) < (self.long_trend_window_size*self.frequency + 1):
            self.am_long.put(tick.last_price)

        if len(self.am_short.queue) < (self.short_trend_window_size*self.frequency + 1):
            self.am_short.put(tick.last_price)

        print(len(self.am_long.queue))
        if len(self.am_long.queue) == self.long_trend_window_size*self.frequency + 1 and len(self.am_short.queue) == self.short_trend_window_size*self.frequency + 1:
            self.on_long_tick()
            self.on_short_tick()
        else:
            return

        if self.dual_side:
            # both long and short
            if self.poster_mode/self.short_trend_window_size > self.buy_threshold:
                if self.pos >= 0:
                    if abs(self.pos) < self.pyramiding:
                        self.buy(tick.last_price, self.fix_size)
                else:
                    self.cover(tick.last_price, abs(self.pos))
                    self.buy(tick.last_price, self.fix_size)


            if self.poster_mode/self.short_trend_window_size < self.sell_threshold:
                if self.pos <= 0:
                    if abs(self.pos) < self.pyramiding:
                        self.short(tick.last_price, self.fix_size)
                else:
                    self.sell(tick.last_price, abs(self.pos))
                    self.short(tick.last_price, self.fix_size)

        else:
            if self.poster_mode/self.short_trend_window_size > self.buy_threshold:
                if self.pos >= 0 and self.pos < self.pyramiding:
                    self.buy(tick.last_price, self.fix_size)

            if self.poster_mode/self.short_trend_window_size < self.sell_threshold:
                if self.pos != 0:
                    self.sell(tick.last_price, self.pos)

        self.am_long.get()
        self.am_short.get()
        self.put_event()


    def on_long_tick(self,):

        binary_sequence = np.where(np.diff(self.am_long.queue) > 0, 1, 0)
        poisson_event = []

        for order in range(self.long_trend_window_size):
            ups = sum(binary_sequence[index] for index in np.arange((order) * self.frequency, (order + 1) * self.frequency, 1))
            poisson_event.append(ups)

        mean = np.mean(poisson_event)
        variance = np.var(poisson_event)

        ## MM estimator
        self.alpha_prior = mean ** 2 / variance
        self.beta_prior = mean / variance

        self.priors_inited = True
        print("computing prior")

        self.put_event()

    def on_short_tick(self,):

        binary_sequence = np.where(np.diff(self.am_short.queue) > 0, 1, 0)
        poisson_event = []

        for order in range(self.short_trend_window_size):
            ups = sum(binary_sequence[index] for index in np.arange((order) * self.frequency, (order + 1) * self.frequency, 1))
            poisson_event.append(ups)

        self.alpha_post = self.alpha_prior + sum(poisson_event)
        self.beta_post = self.beta_prior + self.short_trend_window_size

        # use posterior mean or mode
        self.poster_mean = self.alpha_post/self.beta_post
        self.poster_var = self.alpha_post/(self.beta_post)**2
        self.poster_mode = (self.alpha_post-1)/self.beta_post
        print("computing posterior")
        self.posterior_inited = True
        self.put_event()


