from queue import Queue
from vnpy.trader.object import TickData, Exchange
from datetime import  datetime
import time
am_long = Queue(10)
import random

# for i in range(10):
#     gateway_name = 'OKX'
#     symbol = 'BTC-USDT'
#     exchange = Exchange.OKX
#     datetime = datetime.now()
#     tick = TickData(gateway_name, symbol, exchange, datetime)
#
#     am_long.put(tick)


for i in range(10):

    a = random.randint(0,1)
    am_long.put(a)

am_long
