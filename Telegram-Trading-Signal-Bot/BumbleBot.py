import yfinance as yf
import ta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import datetime as dt
begin_time = dt.datetime.now()

api_key = 'EXAMPLE TELEGRAM KEY'
chat_id = 'EXAMPLE TELEGRAM CHAT ID'
end_point = 'https://api.telegram.org/bot'+api_key+'/sendMessage?chat_id='+chat_id+'&text={}&parse_mode=MarkdownV2'


lookback = dt.datetime.today() - dt.timedelta(days=50)
lookback = lookback.strftime('%Y-%m-%d')
symbols = ['TSLA', 'AMZN', 'AAPL', 'NVDA', 'GOOG', '^GSPC']
names = ['Tesla', 'Amazon', 'Apple', 'Nvidia', 'Google', 'SP500']
# symbols = ['ADA-USD']
# names = ['Cardano']

def Indicators(df):
    df['MACD_diff'] =  ta.trend.macd_diff(df['Close'])
    df['CMFI'] = ta.volume.chaikin_money_flow(df.High, df.Low, df.Close, df.Volume, window=20, fillna=False)
    df['RSI'] = ta.momentum.rsi(df['Close'], window = 14)
    df.dropna(inplace = True)

    return df


for i in symbols:
    end_point = 'https://api.telegram.org/bot'+api_key+'/sendMessage?chat_id='+chat_id+'&text={}&parse_mode=MarkdownV2'
    df = Indicators(yf.download('TSLA', start = lookback, interval='1d')).tail()
    price = str(round(df.Close.iloc[-1],2)).replace('.', '\\.').replace('-', '\\-')
    macd_diff_latest = df.MACD_diff.iloc[-1]
    macd_diff_second_latest = df.MACD_diff.iloc[-2] 
    rsi_1 = round(df.RSI.iloc[-1], 6)
    rsi_2 = round(df.RSI.iloc[-2], 6)
    cmfi_1 = round(df.CMFI.iloc[-1], 6)
    cmfi_2 = round(df.CMFI.iloc[-2], 6)


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


    rsi = str(round(df.RSI.iloc[-1], 6)).replace('.', '\\.').replace('-', '\\-')
    cmfi = str(round(df.CMFI.iloc[-1], 6)).replace('.', '\\.').replace('-', '\\-')
    name_index = symbols.index(i)

    if macd_diff_latest > 0 and macd_diff_second_latest < 0:
        m = f"{names[name_index]} Alert\\! \nThe MACD line has crossed above the signal line, now may be a good time to *BUY {names[name_index]}*\n\n\\-Relative Strength Index: {rsi} \n\\-Chaikin Money Flow Index: {cmfi} \n\\-Has RSI *increased*: {rsi_delta} \n\\-Has Chaikin *increased*: {cmfi_delta} \n\\-Current Price: ${price}"
        end_point = end_point.format(m)
        print('BUY ORDER: ', names[name_index])
        requests.get(end_point)

    if macd_diff_latest < 0 and macd_diff_second_latest > 0:
        m = f"*{names[name_index]} Alert\\!* \nThe MACD line has crossed below the signal line, now may be a good time to *SELL {names[name_index]}*\n\\-Relative Strength Index: {rsi} \n\\-Chaikin Money Flow Index: {cmfi} \n\\-Has RSI *decreased*: {rsi_delta_sell} \n\\-Has Chaikin *decreased*: {cmfi_delta_sell}\n\\-Current Price: ${price}"
        end_point = end_point.format(m)
        print('SELL ORDER: ', names[name_index])
        requests.get(end_point)
    

print('Run sucessfully at: ', dt.datetime.now())
print('run time: ', dt.datetime.now() - begin_time)
print('#################################################################################################################')
print('')
