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

interval_map = {"m": Interval.MINUTE,
                "h": Interval.HOUR,
                "d": Interval.DAILY,
                "t": Interval.TICK}

class DirichletTwo(CtaTemplate):
    author = "Xuanhao"

    prior = 0
    pyramiding = 1
    long_trend_window_size = 5
    short_trend_window_size = 5
    long_trend_period = 1 # 1hour 2hour
    short_trend_period = 5 # 5 minutes
    long_trend_interval = "m"
    short_trend_interval = "m"
    tick_size_threshold = 5
    fix_size = 1
    dual_side = 1
    poster_mode = 0
    parameters = ["dual_side", "pyramiding", "long_trend_window_size","short_trend_window_size","long_trend_period", "short_trend_period" ,"fix_size", "long_trend_interval", "short_trend_interval","tick_size_threshold"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        long_interval = interval_map[self.long_trend_interval]
        short_interval = interval_map[self.short_trend_interval]

        self.bg_long = BarGenerator(self.on_bar, self.long_trend_period, self.on_long_bar, interval=long_interval)
        self.bg_short = BarGenerator(self.on_bar, self.short_trend_period, self.on_short_bar, interval=short_interval)
        self.am_long = ArrayManager(self.long_trend_window_size)
        self.am_short = ArrayManager(self.short_trend_window_size)
        self.tick_size = self.get_pricetick()

        self.prior_bullish = 0
        self.prior_bearish = 0
        self.prior_neutral = 0

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

        # 计算看涨、看跌和中性的Bar数量
        for i in range(self.am_long.size):
            diff = self.am_long.close[i] - self.am_long.open[i]
            tick_diff = diff/self.tick_size
            if tick_diff > self.tick_size_threshold:
                self.prior_bullish += 1
            elif tick_diff < -self.tick_size_threshold:
                self.prior_bearish += 1
            else:
                self.prior_neutral += 1

        self.prior_neutral = self.prior_neutral/self.am_long.size
        self.prior_bearish = self.prior_bearish/self.am_long.size
        self.prior_bullish = self.prior_bullish/self.am_long.size

        self.priors_inited = True

    def on_short_bar(self, short_bar: BarData):
        self.am_short.update_bar(short_bar)
        if not self.am_short.inited:
            return

        if not self.priors_inited:
            return

        buy_signal = False
        sell_signal = False

        bullish_count = 0
        bearish_count = 0
        neutral_count = 0

        # 计算看涨、看跌和中性的Bar数量
        for i in range(self.am_short.size):
            diff = self.am_short.close[i] - self.am_short.open[i]
            tick_diff = diff/self.tick_size
            if tick_diff > self.tick_size_threshold:
                bullish_count += 1
            elif tick_diff < -self.tick_size_threshold:
                bearish_count += 1
            else:
                neutral_count += 1

        # 更新参数
        self.post_bullish = self.prior_bullish + bullish_count
        self.post_bearish = self.prior_bearish + bearish_count
        self.post_neutral = self.prior_neutral + neutral_count

        sumpost = self.post_bearish+self.post_neutral+self.post_bullish

        post_prob_bull = self.post_bullish/sumpost
        post_prob_bear = self.post_bearish/sumpost
        post_prob_neu = self.post_neutral/sumpost


        maxValue = max(post_prob_neu,post_prob_bull,post_prob_bear)

        if maxValue == post_prob_bear:
            sell_signal = True
        elif maxValue == post_prob_bull:
            buy_signal = True
        else:
            return

        if self.dual_side:
            if buy_signal and sell_signal:
                return
            # both long and short
            if buy_signal:
                if self.pos >= 0:
                    if abs(self.pos) < self.pyramiding:
                        self.buy(short_bar.close_price, self.fix_size)
                else:
                    self.cover(short_bar.close_price, abs(self.pos))
                    self.buy(short_bar.close_price, self.fix_size)

            if sell_signal:
                if self.pos <= 0:
                    if abs(self.pos) < self.pyramiding:
                        self.short(short_bar.close_price, self.fix_size)
                else:
                    self.sell(short_bar.close_price, abs(self.pos))
                    self.short(short_bar.close_price, self.fix_size)

        else:
            if buy_signal:
                if self.pos >= 0 and self.pos < self.pyramiding:
                    self.buy(short_bar.close_price, self.fix_size)

            if sell_signal:
                if self.pos != 0:
                    self.sell(short_bar.close_price, self.pos)
