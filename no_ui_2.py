from logging import INFO
from vnpy.trader.setting import SETTINGS
from vnpy_ctastrategy.backtesting import BacktestingEngine
from datetime import datetime
from vnpy.trader.object import Interval
from vnpy_ctastrategy.strategies.psignal_strategy import Psignal
from pandas import DataFrame
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import multiprocessing
import plotly.io as pio



SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True

bt_parameters = {
    'vt_symbol' : 'BTCUSDT.BINANCE',
    'interval' : Interval.MINUTE,
    'start' : datetime(2021,7,1),
    'rate' : 0.0005,
    'slippage' : 0,
    'size' : 1,
    'pricetick' : 0.1,
    'capital' : 1000000,
    'end': datetime(2022,7,1)
}


class btEngine(BacktestingEngine):

    def show_chart(self, df: DataFrame = None, cta_setting: dict = None) -> None:
        # Check DataFrame input exterior
        if df is None:
            df: DataFrame = self.daily_df

        # Check for init DataFrame
        if df is None:
            return

        fig = make_subplots(
            rows=4,
            cols=1,
            subplot_titles=["Balance", "Drawdown", "Daily Pnl", "Pnl Distribution"],
            vertical_spacing=0.06
        )

        balance_line = go.Scatter(
            x=df.index,
            y=df["balance"],
            mode="lines",
            name="Balance"
        )

        drawdown_scatter = go.Scatter(
            x=df.index,
            y=df["drawdown"],
            fillcolor="red",
            fill='tozeroy',
            mode="lines",
            name="Drawdown"
        )
        pnl_bar = go.Bar(y=df["net_pnl"], name="Daily Pnl")
        pnl_histogram = go.Histogram(x=df["net_pnl"], nbinsx=100, name="Days")

        fig.add_trace(balance_line, row=1, col=1)
        fig.add_trace(drawdown_scatter, row=2, col=1)
        fig.add_trace(pnl_bar, row=3, col=1)
        fig.add_trace(pnl_histogram, row=4, col=1)

        fig.update_layout(height=1000, width=1000)

        n_points = cta_setting['n_points']
        time_frame = cta_setting['time_frame']
        fig.write_html(f'./backtest_results/graphs/nPoints_{n_points}_timeframe_{time_frame}.html')

        # pio.write_image(fig, f'./backtest_results/graphs/nPoints_{n_points}_timeframe_{time_frame}.png')
        # fig.show()

def init_engine():
    global btEngine
    btEngine = btEngine()
    btEngine.set_parameters(vt_symbol=bt_parameters['vt_symbol'],
                        interval=bt_parameters['interval'],
                        start=bt_parameters['start'],
                        end=bt_parameters['end'],
                        rate=bt_parameters['rate'],
                        slippage=bt_parameters['slippage'],
                        size=bt_parameters['size'],
                        capital=bt_parameters['capital'],
                        pricetick=bt_parameters['pricetick']
                        )
    btEngine.load_data()


def run_backtest_multi(cta_setting:dict):
    btEngine.add_strategy(Psignal, cta_setting)
    btEngine.run_backtesting()
    btEngine.calculate_result()
    stat = btEngine.calculate_statistics()
    n_points = cta_setting['n_points']
    time_frame = cta_setting['time_frame']
    stat['name'] = f'nPoints_{n_points}_timeframe_{time_frame}'
    btEngine.show_chart(cta_setting=cta_setting)
    stat = pd.DataFrame([stat])
    stat.to_csv(f'./backtest_results/statistics/nPoints_{n_points}_timeframe_{time_frame}.csv', index=False, header=False)
    print(f'nPoints_{n_points}_timeframe_{time_frame}')
    btEngine.clear_data()

    # btEngine.show_chart()
n_points_range = [13,21,34,55,89,144,233,377,610,987,1597]
# time_frame = [5] # w8
time_frame = [15] # w5
# time_frame = [30] # w4
# time_frame = [45, 60, 120, 240] # w3

setting_lists = []
for n_point in n_points_range:
    for tf in time_frame:
        cta_setting = {
            "n_points": n_point,
            "fixed_size": 1,
            "time_frame": tf,
        }
        setting_lists.append(cta_setting)

# btEngine.load_data()

# run_backtest_multi(setting_lists[5])
init_engine()
# Determine the number of processes to use

def main():
    setting_lists = []
    for n_point in n_points_range:
        for tf in time_frame:
            cta_setting = {
                "n_points": n_point,
                "fixed_size": 1,
                "time_frame": tf,
            }
            setting_lists.append(cta_setting)
    num_processes = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(run_backtest_multi, setting_lists)

if __name__ == '__main__':

    # multiprocessing.freeze_support()  # Only necessary if you're freezing your program with something like PyInstaller
    # main()
    for setting in setting_lists:
        run_backtest_multi(setting)
