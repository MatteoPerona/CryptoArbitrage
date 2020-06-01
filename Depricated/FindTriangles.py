import ccxt

import matplotlib.pyplot as plt 
from matplotlib import style
import numpy as np
import pandas as pd

import math
import csv

import time
import multiprocessing 


exchange_id = 'binanceus'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': 'sbne6lN7qdZDoj4bSGiL368N81sOQnf37bPvb9Nu6QvX7HDMgaLSjsnYZEnx8IJA',
    'secret': 'jdP302v02pPYRvhzr7CUtmXNOgyEc6V3K4FyJ8mOPsSQOQ8cvDGWHA37viU4Ta5U',
    'timeout': 30000,
    'enableRateLimit': True,
})

new = True


def lastTrade(ticker):
    exchange.load_markets ()
    return pd.DataFrame(exchange.fetch_trades(ticker)).tail(1)

def lt(ticker):
    for key in exchange.fetch_trades(ticker):
        print(key)

BTCMarket = ['ETH/BTC', 'XRP/BTC', 'BNB/BTC', 'LTC/BTC', 'BCH/BTC']
USDTMarket = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'BCH/USDT', 'LTC/USDT', 'BNB/USDT', 'ADA/USDT', 'BAT/USDT', 'ETC/USDT', 'XLM/USDT', 'ZRX/USDT', 'DOGE/USDT', 'ATOM/USDT', 'NEO/USDT', 'VET/USDT', 'QTUM/USDT', 'ONT/USDT']
BUSDMarket = ['BTC/BUSD', 'ZIL/BUSD', 'BNB/BUSD', 'XRP/BUSD', 'ETH/BUSD', 'ALGO/BUSD', 'XTZ/BUSD']
USDMarket = ['BTC/USD', 'ETH/USD', 'XRP/USD', 'BCH/USD', 'LTC/USD', 'USDT/USD', 'BNB/USD', 'ADA/USD', 'BAT/USD', 'ETC/USD', 'XLM/USD', 'ZRX/USD', 'LINK/USD', 'RVN/USD', 'DASH/USD', 'ZEC/USD', 'ALGO/USD', 'IOTA/USD', 'BUSD/USD', 'WAVES/USD', 'ATOM/USD', 'NEO/USD', 'QTUM/USD', 'NANO/USD', 'ICX/USD', 'ENJ/USD', 'ONT/USD', 'ZIL/USD', 'VET/USD', 'XTZ/USD']
def updateMarketLists():
    df = pd.DataFrame(exchange.fetch_markets())
    global BTCMarket
    global USDTMarket
    global BUSDMarket
    global USDMarket
    for index, row in df.iterrows():
        if '/USDT' in row['symbol']:
            USDTMarket.append(row['symbol'])
        elif '/BUSD' in row['symbol']:
            BUSDMarket.append(row['symbol'])
        elif '/BTC' in row['symbol']:
            BTCMarket.append(row['symbol'])
        else:
            USDMarket.append(row['symbol'])

if new:
    with open('usdtbtc.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ETH/BTC', 'XRP/BTC', 'BNB/BTC', 'LTC/BTC', 'BCH/BTC'])

def USDTtoBTC():
    aList = []
    for symbol in BTCMarket:
        c1=lastTrade(symbol[0:3]+'/USDT')['price']
        c2=lastTrade('BTC/USDT')['price']
        c3=lastTrade(symbol)['price']
        p=((c1*(math.pow(c2, -1)))-c3)*c2
        v=p.values
        aList.append(v[0])
    with open('usdtbtc.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(aList)

def graphUSDTtoBTC():
    df = pd.read_csv('usdtbtc.csv')
    print(df)
    ax=plt.gca()
    df.plot(kind='line', y='ETH/BTC', ax=ax)
    df.plot(kind='line', y='XRP/BTC', color='red', ax=ax)
    df.plot(kind='line', y='BNB/BTC', color='green', ax=ax)
    df.plot(kind='line', y='LTC/BTC', color='purple', ax=ax)
    df.plot(kind='line', y='BCH/BTC', color='purple', ax=ax)
    plt.show()

def main():
    try:
     while True:
         USDTtoBTC()
    except KeyboardInterrupt:
        print('KeyboardInterrupt: No longer collecting')


if __name__ == "__main__":
    #debug USDtoBTC collection
    '''start = time.time()
    for x in range(2):
        USDTtoBTC()
    end = time.time()
    print(end-start)
    graphUSDTtoBTC()'''

    #main()
    main()
