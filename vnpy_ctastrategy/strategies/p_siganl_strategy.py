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

import talib
import numpy as np

class PSignalStrategy(CtaTemplate):
    """"""

    author = "xuanhao"

    # Parameters and constants of P-Signal
    nPoints = 9
    fixed_size = 1

    parameters = ["nPoints", "fixed_size"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager((self.nPoints)*2)

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(1000)
        self.nIntr = self.nPoints - 1

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


    def on_bar(self, bar: BarData):
        """
        Callback of new 1-minute bar data update.
        """
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        # fPSignal = self.fPSignal(np.diff(self.ohlc4()), self.nIntr)
        nPSignal:np.ndarray = talib.SMA(self.fPSignal(np.diff(self.ohlc4()), self.nIntr), self.nIntr)
        ndPSignal = self.sign((nPSignal[-1] - nPSignal[-2]))
        nPSignal = nPSignal[-1]

        print(f"nPSignal{nPSignal}, ndPSignal{ndPSignal}")
        # Strategy logic
        if nPSignal < 0 and ndPSignal > 0 and self.pos == 0:
            self.buy(bar.close_price, volume=self.fixed_size)
            print(f"buy {self.fixed_size}, at price: {bar.close_price}, position{self.pos}")

        elif nPSignal > 0 and ndPSignal < 0 and self.pos != 0 :
            print(f"cover {self.pos}, at price: {bar.close_price}, position{self.pos}")
            self.sell(bar.open_price, self.pos)


    def fPSignal(self, array:np.ndarray, size:int)->np.ndarray:

        nStDev = talib.STDDEV(array, size, 1)
        nSma = talib.SMA(array, size)

        # 去除包含NaN值的元素
        valid_indices = ~np.isnan(nStDev) & ~np.isnan(nSma)
        nStDev = nStDev[valid_indices]
        nSma = nSma[valid_indices]

        fErf_vectorized = np.vectorize(self.fErf)
        sign_vectorized = np.vectorize(self.sign)

        nPSignal = np.where(nStDev > 0, fErf_vectorized(nSma / nStDev / (np.sqrt(2))), sign_vectorized(nSma) * 1.0)

        return nPSignal

    def ohlc4(self,) ->np.ndarray:
        o = self.am.open_array
        h = self.am.high_array
        l = self.am.low_array
        c = self.am.close_array
        average_array = np.mean([o, h, l, c], axis=0)
        return average_array

    def fErf(self, x):
        """
        Horner's method for the error (Gauss) & P-Signal functions.
        """
        nT = 1.0 / (1.0 + 0.5 * abs(x))
        nAns = (
                1.0 - nT * np.exp(-x * x - 1.26551223 +
                nT * (1.00002368 + nT * (0.37409196 +
                nT * (0.09678418 + nT * (-0.18628806 +
                nT * (0.27886807 + nT * (-1.13520398 +
                nT * (1.48851587 + nT * (-0.82215223 +
                nT * (0.17087277)))))))))))
        return nAns if x >= 0 else -nAns

    def sign(self, value):
        if value == 0:
            return 0
        elif value > 0:
            return 1
        else:
            return -1


    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass