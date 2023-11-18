from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy.trader.object import Interval
from datetime import datetime
from vnpy_ctastrategy.strategies import p_siganl_strategy


if __name__ == '__main__':
    engine = BacktestingEngine()

    # engine.set_parameters(
    #     vt_symbol=ETH,
    #     interval=,
    #     start=,
    #     end=,
    #     slippage=,
    #     size=,
    #     pricetick=,
    #     capital=,
    # )