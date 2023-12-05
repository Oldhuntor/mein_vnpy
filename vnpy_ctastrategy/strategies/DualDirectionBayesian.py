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
from queue import Queue
from datetime import datetime
from vnpy.trader.object import Interval
class DualDirectionBayesian(CtaTemplate):
    author = "Xuanhao"

    priorUp = 0
    priorDown = 0
    posteriorUp = 0
    posteriorDown = 0
    long_trend_window_size = 5
    short_trend_window_size = 5
    long_trend_period = 60
    short_trend_period = 5
    fix_size = 1
    parameters = ["long_trend_window_size","short_trend_window_size","long_trend_period", "short_trend_period" ,"fix_size"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        if self.long_trend_period >= 5:
            self.bg_long = BarGenerator(self.on_bar, self.long_trend_period, self.on_long_bar)
        else:
            self.bg_long = BarGenerator(self.on_bar, self.long_trend_period, self.on_long_bar, interval=Interval.HOUR)

        self.bg_short = BarGenerator(self.on_bar, self.short_trend_period, self.on_short_bar)
        self.am_long = ArrayManager(self.long_trend_window_size)
        self.am_short = ArrayManager(self.short_trend_window_size)
        self.postUpArray = Queue(2)
        self.postDownArray = Queue(2)
        self.last_trade = "sell"


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
        # update prior
        self.priorUp = ups/self.long_trend_window_size
        self.priorDown = 1 - (ups/self.long_trend_window_size)
        # print(f"long: {long_bar}")

    def on_short_bar(self, short_bar: BarData):
        self.am_short.update_bar(short_bar)
        if not self.am_short.inited:
            return

        # print(f"short: {short_bar}")
        ups = sum(1 for index in range(self.am_short.size) if self.am_short.close_array[index] > self.am_short.open_array[index])
        downs = self.am_short.size - ups
        likelihoodUp = self.compute_likelihoodUp(ups)
        likelihoodDown = self.compute_likelihoodDown(downs)

        p_D_Up = self.compute_normalizing_constant(ups)
        p_D_Down = self.compute_normalizing_constant(downs)
        self.posteriorUp = round(likelihoodUp * self.priorUp / p_D_Up, 3)
        self.posteriorDown = round(likelihoodDown * self.priorDown / p_D_Down, 3)

        self.postUpArray.put(self.posteriorUp)
        self.postDownArray.put(self.posteriorDown)

        if len(self.postUpArray.queue) < 2:
            return

        prePosterUp = self.postUpArray.get()
        prePosterDown = self.postDownArray.get()

        currentPosterUp = self.posteriorUp
        currentPosterDown = self.posteriorDown

        msg = f"{short_bar.datetime}, {currentPosterUp}, {currentPosterDown}"
        # print(msg)
        # self.logging(msg)


        # long logic
        if prePosterUp <= prePosterDown and currentPosterUp > currentPosterDown and self.last_trade == "sell":
            self.buy(short_bar.close_price, self.fix_size)
            msg = f"{short_bar.datetime},{prePosterUp}, {prePosterDown}, {currentPosterUp}, {currentPosterDown}, buy"
            # self.logging(msg)
            self.last_trade = 'buy'

        # short logic
        if prePosterUp >= prePosterDown and currentPosterUp < currentPosterDown and self.last_trade == "buy":
            self.sell(short_bar.close_price, self.fix_size)
            msg = f"{short_bar.datetime},{prePosterUp}, {prePosterDown}, {currentPosterUp}, {currentPosterDown}, sell"
            # self.logging(msg)
            self.last_trade = 'sell'

    def compute_likelihoodUp(self, ups):
        likelihood:float = binom.pmf(ups, self.am_short.size, self.priorUp)
        return likelihood

    def compute_likelihoodDown(self, downs):
        likelihood:float = binom.pmf(downs, self.am_short.size, self.priorDown)
        return likelihood

    def compute_normalizing_constant(self, num):
        """
        Compute the normalizing constant p(D) using a sequence of prior values.
        """
        prior_values = np.linspace(0, 1, self.long_trend_window_size)
        p_D = sum(binom.pmf(num, self.am_short.size, prior) * prior for prior in prior_values)
        return p_D


    def on_order(self, order):
        pass

    def on_trade(self, trade):
        pass

    def on_stop_order(self, stop_order):
        pass

    def logging(self, msg: str) -> None:
        with open('/Users/huangxuanhao/Desktop/MyProject/mein_vnpy/output.txt', 'a') as file:
            file.write(msg + '\n')
