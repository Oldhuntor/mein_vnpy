import matplotlib.pyplot as plt
import pandas as pd

file = '/Users/huangxuanhao/Desktop/MyProject/mein_vnpy/db/Psignal.csv'

market = '/Users/huangxuanhao/Desktop/MyProject/mein_vnpy/db/BTC-USDT.okx.csv'
signal = pd.read_csv(file)
market = pd.read_csv(market)
plt.plot(market)
plt.plot(signal)
plt.show()