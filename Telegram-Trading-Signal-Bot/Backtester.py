import yfinance as yf
import ta
import pandas 
import matplotlib.pyplot as plt
import numpy as np



df = yf.download('BTC-USD', start = '2021-12-01', interval='1h')

def Indicators(df):
    df['MACD'] =  ta.trend.macd_diff(df['Close'])
    df['CMFI'] = ta.volume.chaikin_money_flow(df.High, df.Low, df.Close, df.Volume, window=20, fillna=False)
    df['rsi'] = ta.momentum.rsi(df['Close'], window = 14)
    df.dropna(inplace = True)
    return df

df = Indicators(df)

buy,sell = [], []

open_position = False
for i in range(2, len(df.index)):
    if open_position == False and df.CMFI[i] > 0.1 and df.MACD.iloc[i] > 0 and df.MACD.iloc[i-1] < 0:
        buy.append(i)
        open_position = True

    elif open_position == True and df.MACD.iloc[i] < 0 and df.MACD.iloc[i-1] > 0 and df.rsi[i] > 60 and df.CMFI[i] > 0.1 :
        sell.append(i)
        open_position = False



plt.scatter(df.iloc[buy].index, df.iloc[buy]['Adj Close'], marker='x', color = 'green')
plt.scatter(df.iloc[sell].index, df.iloc[sell]['Adj Close'], marker='x', color = 'red')
plt.plot(df['Adj Close'], label = 'Close', color = 'k')
plt.legend()
plt.show()

real_buy = [i+1 for i in buy]
real_sell = [i+1 for i in sell]

buy_prices = df.Open.iloc[real_buy]
sell_prices = df.Open.iloc[real_sell]


if sell_prices.index[0] < buy_prices.index[0]:
    print('dropped first record because it was a sell')
    sell_prices = sell_prices.drop(sell_prices.index[0])

elif buy_prices.index[-1] > sell_prices.index[-1]:
    print('dropped last reccord because it was a buy')
    buy_prices = buy_prices.drop(buy_prices.index[-1])

profits = []


for i in range(min([len(sell_prices.values), len(buy_prices.values)])):
    profits.append((sell_prices.values[i] - buy_prices.values[i])/buy_prices.values[i])

grow = 1
gs = []
for i in profits:
    grow = (i+1)*grow
    gs.append(grow)


print('mean profit per trade: ', np.mean(profits))
print('number of trades: ', len(profits))
print('growth of starting capital: ', grow)
print('market growth: ', df['Adj Close'].values[-1]/df['Adj Close'].values[0])
