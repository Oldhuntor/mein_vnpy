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
from scipy.stats import binom,beta,norm
import pandas as pd
from statsmodels.sandbox.stats.runs import runstest_1samp
from queue import Queue
class RuntestStrategy(CtaTemplate):
    author = "Xuanhao"

    pyramiding = 1
    long_trend_window_size = 5
    short_trend_window_size = 5
    long_trend_period = 60
    short_trend_period = 5
    fix_size = 1
    dual_side = 1
    longP = 0
    shortP = 0
    parameters = ["dual_side", "pyramiding", "long_trend_window_size","short_trend_window_size","long_trend_period", "short_trend_period" ,"fix_size"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg_long = BarGenerator(self.on_bar, self.long_trend_period, self.on_long_bar)
        self.bg_short = BarGenerator(self.on_bar, self.short_trend_period, self.on_short_bar)
        self.am_long = ArrayManager(self.long_trend_window_size)
        self.am_short = ArrayManager(self.short_trend_window_size)
        self.longQ = Queue(self.long_trend_period)
        self.shortQ = Queue(self.short_trend_period)
        self.longP_inited = False

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

        _, pVal = runstest_1samp(self.am_long.close_array)
        self.longP = pVal

        if len(self.longQ.queue) < self.long_trend_period:
            self.longQ.put(pVal)
            return

        self.longQ.get()
        self.longQ.put(pVal)
        self.longP_inited = True

    def on_short_bar(self, short_bar: BarData):
        self.am_short.update_bar(short_bar)
        if not self.am_short.inited:
            return

        _, pVal = runstest_1samp(self.am_short.close_array)
        self.shortP = pVal

        if len(self.shortQ.queue) < self.short_trend_period:
            self.shortQ.put(pVal)
            return

        if not self.longP_inited:
            return

        self.shortQ.get()
        self.shortQ.put(pVal)

        longUps = sum(1 for index in range(self.am_long.size) if self.am_long.close_array[index] > self.am_long.open_array[index])
        shortUps = sum(1 for index in range(self.am_short.size) if self.am_short.close_array[index] > self.am_short.open_array[index])

        if (longUps + shortUps) / (self.am_long.size + self.am_short.size) > 0.5:
            signal = "long"
        else:
            signal = "short"

        # 短周期p值更小时，强烈趋势信号，开仓
        if self.longQ.queue[-1] > self.shortQ.queue[-1]:
            if signal == "long":
                if self.pyramiding > self.pos > 0:
                    self.buy(short_bar.close_price, self.fix_size)
                elif self.pos < 0 :
                    self.cover(short_bar.close_price, abs(self.pos))
                    self.buy(short_bar.close_price, self.fix_size)
            else:
                if self.pos > 0:
                    self.sell(short_bar.close_price, self.pos)
                    self.short(short_bar.close_price, self.fix_size)
                elif abs(self.pos) < self.pyramiding:
                    self.short(short_bar.close_price, self.fix_size)

        # 短周期p值大时，趋势停止信号，平仓
        elif self.longQ.queue[-1] < self.shortQ.queue[-1]:
            if self.pos != 0:
                if self.pos > 0 :
                    self.sell(short_bar.close_price, self.pos)

                else:
                    self.cover(short_bar.close_price, abs(self.pos))

    def on_order(self, order):
        pass

    def on_trade(self, trade):
        pass

    def on_stop_order(self, stop_order):
        pass
