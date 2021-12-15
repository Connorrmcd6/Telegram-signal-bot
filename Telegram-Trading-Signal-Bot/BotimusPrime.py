import yfinance as yf
import ta
import requests
import datetime as dt
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from time import sleep
begin_time = dt.datetime.now()

telegram_api_key = 'EXAMPLE TELEGRAM KEY'
chat_id = 'EXAMPLE TELEGRAM CHAT ID'
api_key = 'EXAMPLE BINANCE KEY'
api_secret = 'EXAMPLE BINANCE API SECRET'
client = Client(api_key, api_secret)


symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT', 'LTCUSDT', 'BCHUSDT', 'SOLUSDT', 'DOTUSDT', 'ENSUSDT',
 'AVAXUSDT', 'MATICUSDT']

names = ['Bitcoin', 'Ethereum', 'Cardano', 'Ripple', 'Dogecoin', 'Litecoin', 'Bitcoin Cash', 'Solana', 'Polkadot', 'ENS Tokens',
 'Avalanche', 'Polygon']

def get_all_data(symbols, interval, lookback):
    dfdict = {}
    for i in symbols: 
        key = i
        try:
            df = pd.DataFrame(client.get_historical_klines(i,  str(interval), str(lookback)+' ago UTC'))
        except BinanceAPIException as e:
            print(e)
            df = pd.DataFrame(client.get_historical_klines(i,  str(interval), str(lookback)+' ago UTC'))
        df = df.iloc[:, :6]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df['Time'] = pd.to_datetime(df['Time'],unit='ms')
        df['Open'] = pd.to_numeric(df["Open"], downcast="float")
        df['Close'] = pd.to_numeric(df["Close"], downcast="float")
        df['High'] = pd.to_numeric(df["High"], downcast="float")
        df['Low'] = pd.to_numeric(df["Low"], downcast="float")
        df['Volume'] = pd.to_numeric(df["Volume"], downcast="float")
        df.set_index('Time', drop=True)
        df['MACD_diff'] =  ta.trend.macd_diff(df['Close'])
        df['RSI'] = ta.momentum.rsi(df.Close, window = 14)
        df['CMFI'] = ta.volume.chaikin_money_flow(df.High, df.Low, df.Close, df.Volume, window=20, fillna=False)
        df.dropna(inplace = True)
        dfdict[key] = df
    return dfdict

dfdict = get_all_data(symbols, '1h', '2 day')
n = 0
for df in dfdict:
    end_point = 'https://api.telegram.org/bot'+telegram_api_key+'/sendMessage?chat_id='+chat_id+'&text={}&parse_mode=MarkdownV2'
    price = str(round(dfdict[df].Close.iloc[-1], 8)).replace('.', '\\.').replace('-', '\\-')
    macd_diff_latest = dfdict[df].MACD_diff.iloc[-1]
    macd_diff_second_latest = dfdict[df].MACD_diff.iloc[-2] 
    rsi_1 = round(dfdict[df].RSI.iloc[-1], 6)
    rsi_2 = round(dfdict[df].RSI.iloc[-2], 6)
    cmfi_1 = round(dfdict[df].CMFI.iloc[-1], 6)
    cmfi_2 = round(dfdict[df].CMFI.iloc[-2], 6)

    if rsi_1 > rsi_2:
        rsi_delta = 'Yes'
        rsi_delta_sell = 'No'
    else:
        rsi_delta_sell = 'Yes'
        rsi_delta ='No'

    if cmfi_1 > cmfi_2:
        cmfi_delta = 'Yes'
        cmfi_delta_sell = 'No'
    else:
        cmfi_delta = 'No'
        cmfi_delta_sell = 'Yes'


    rsi = str(round(dfdict[df].RSI.iloc[-1], 6)).replace('.', '\\.').replace('-', '\\-')
    cmfi = str(round(dfdict[df].CMFI.iloc[-1], 6)).replace('.', '\\.').replace('-', '\\-')
    name= names[n]
    n +=1

    if macd_diff_latest > 0 and macd_diff_second_latest < 0 and cmfi_1 > 0.1:
        m = f"{name} Alert\\! \nThe MACD line has crossed above the signal line, now may be a good time to *BUY {name}*\n\n\\-Relative Strength Index: {rsi} \n\\-Chaikin Oscillator: {cmfi} \n\\-Has RSI *increased*: {rsi_delta} \n\\-Has Chaikin *increased*: {cmfi_delta} \n\\-Current Price: ${price}"
        end_point = end_point.format(m)
        print('BUY ORDER:', name)
        requests.get(end_point)

    if macd_diff_latest < 0 and macd_diff_second_latest > 0 and  rsi_1 > 60 and cmfi_1 > 0.1:
        m = f"*{name} Alert\\!* \nThe MACD line has crossed below the signal line, now may be a good time to *SELL {name}*\n\\-Relative Strength Index: {rsi} \n\\-Chaikin Oscillator: {cmfi} \n\\-Has RSI *decreased*: {rsi_delta_sell} \n\\-Has Chaikin *decreased*: {cmfi_delta_sell}\n\\-Current Price: ${price}"
        end_point = end_point.format(m)
        print('SELL ORDER:', name)
        requests.get(end_point)


print('Run successfully at: ', dt.datetime.now())
print('run time: ', dt.datetime.now() - begin_time)
print('#################################################################################################################')
print('')