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
import talib

class Psignal(CtaTemplate):
    author = "xuanhao"

    n_points = 9
    fixed_size = 1
    time_frame = 5
    parameters = ["n_points", "fixed_size", "time_frame"]
    variables = ["n_psignal", "nd_psignal"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, self.time_frame, self.on_k_bar)
        self.am = ArrayManager(size=self.n_points*2)  # 需要足够的窗口大小来计算指标
        self.last_trade = "sell"

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")
        self.put_event()

    def on_tick(self, tick):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_k_bar(self, bar: BarData):
        """
        通用 对不同粒度对K线操作
        """
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        ohlc4 = (self.am.open_array + self.am.high_array +
                 self.am.low_array + self.am.close_array) / 4
        ohlc4_changes = np.diff(ohlc4)

        f_psignal = self.f_psignal(ohlc4_changes, self.n_points-1)

        if len(f_psignal):
            n_psignal = talib.SMA(self.f_psignal(ohlc4_changes, self.n_points-1), self.n_points-1)
            nd_psignal = np.sign(n_psignal[-1] - n_psignal[-2])

            if n_psignal[-1] < 0 and nd_psignal > 0 and self.last_trade == "sell":
                self.buy(bar.close_price, self.fixed_size)
                self.last_trade = "buy"

            elif n_psignal[-1] > 0 and nd_psignal < 0 and self.last_trade == "buy" :
                self.sell(bar.close_price, self.pos)
                self.last_trade = "sell"


    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)

    def f_erf(self, x):
        nT = 1.0/(1.0 + 0.5*np.abs(x))
        nAns = 1.0 - nT*np.exp(-x*x - 1.26551223 +
            nT*( 1.00002368 + nT*( 0.37409196 + nT*( 0.09678418 +
            nT*(-0.18628806 + nT*( 0.27886807 + nT*(-1.13520398 +
            nT*( 1.48851587 + nT*(-0.82215223 + nT*( 0.17087277 ))))))))))
        return nAns if x >= 0 else -nAns

    def f_psignal(self, ser, int_size):
        n_stdev = talib.STDDEV(ser, int_size)
        n_sma = talib.SMA(ser, int_size)
        valid_indices = ~np.isnan(n_stdev) & ~np.isnan(n_sma)
        n_stdev = n_stdev[valid_indices]
        n_sma = n_sma[valid_indices]

        if 0 in n_stdev:
            return []

        return np.where(n_stdev > 0, np.vectorize(self.f_erf)(n_sma/n_stdev/np.sqrt(2)), np.sign(n_sma))

    def on_order(self, order):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order):
        """
        Callback of stop order update.
        """
        pass
