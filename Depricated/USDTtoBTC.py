import ccxt

import matplotlib.pyplot as plt 
from matplotlib import style
import pandas as pd

import math
import csv

import time
from datetime import datetime

from multiprocessing import Pool



exchange_id = 'binanceus'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': 'sbne6lN7qdZDoj4bSGiL368N81sOQnf37bPvb9Nu6QvX7HDMgaLSjsnYZEnx8IJA',
    'secret': 'jdP302v02pPYRvhzr7CUtmXNOgyEc6V3K4FyJ8mOPsSQOQ8cvDGWHA37viU4Ta5U',
    'timeout': 30000,
    'enableRateLimit': True,
})


BTCMarket = ['ETH/BTC', 'XRP/BTC', 'BNB/BTC', 'LTC/BTC', 'BCH/BTC']
USDTMarket = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'BCH/USDT', 'LTC/USDT', 'BNB/USDT', 'ADA/USDT', 'BAT/USDT', 'ETC/USDT', 'XLM/USDT', 'ZRX/USDT', 'DOGE/USDT', 'ATOM/USDT', 'NEO/USDT', 'VET/USDT', 'QTUM/USDT', 'ONT/USDT']
wallet = 'wallet.csv'
cash = 5
delay = 1
fee = .00075

def lastTrade(ticker):
    data = exchange.fetch_trades(ticker)
    return data[-1]['price']

def discrepancy(market):
    c1=lastTrade(market[0:3]+'/USDT')
    c2=lastTrade('BTC/USDT')
    c3=lastTrade(market)
    r=(c1*(math.pow(c2, -1))-c3)*c2
    return r

def discrep_process():
    p = Pool()
    result = p.map(discrepancy,BTCMarket)
    p.close()
    p.join()
    return result

def high():
    max = 0
    min = 0
    iter = 0
    mxC = 0
    mnC = 0
    discrepList = discrep_process()
    print(f'discepancies: {discrepList}')
    for price in discrepList:
        if price > max:
            max = price
            mxC = iter
        elif price < min:
            min = price
            mnC = iter
        iter+=1
    if abs(min) > max:
        print(f'coin is: {BTCMarket[mnC][0:3]}/USDT, discrepancy is: ${min}')
        return [BTCMarket[mnC][0:3]+'/USDT', min]
    print(f'coin is: {BTCMarket[mnC][0:3]}/USDT, discrepancy is: ${max}')
    return [BTCMarket[mxC][0:3]+'/USDT', max]

def newWallet():
    now = datetime.now()
    time_now = now.strftime('%H:%M:%S')
    with open(wallet, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Coin', 'Cash'])
        writer.writerow([time_now, 'none', cash])

def arbitrage():
    global cash
    listvar = high()
    now = datetime.now()
    time_now = now.strftime('%H:%M:%S')
    totFee = cash*fee*3
    print(f'fee is {totFee}')
    coins_to_buy = cash/lastTrade(listvar[0])
    print(f'buying {coins_to_buy} {listvar[0]}')
    discrepancyNow = abs(listvar[1])
    cash = (coins_to_buy*discrepancyNow)-totFee
    with open(wallet, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time_now, listvar[0], cash])

def main(verbose=True):
    newWallet()
    try:
        while True:
            if verbose:
                start = time.time()
                oldCash = cash
            
            arbitrage()

            if verbose:
                end = time.time()
                print(f'Calculations took: {int(end-start)} seconds')
                print(f'You made: ${round(cash-oldCash, 2)} and now have ${round(cash, 2)}')

            time.sleep(delay)

    except KeyboardInterrupt:
        print('KeyboardInterrupt: No longer collecting')


def staticDraw():
    plt.style.use('fivethirtyeight')
    df = pd.read_csv(wallet)
    df.plot(x='Time', y='Cash')
    plt.show()

if __name__ == "__main__":
    main()
    #staticDraw()


