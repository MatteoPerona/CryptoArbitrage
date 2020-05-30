import ccxt

import numpy as np 
import time
from datetime import datetime
import csv

from multiprocessing import Pool


exchange_id = 'binanceus'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': 'sbne6lN7qdZDoj4bSGiL368N81sOQnf37bPvb9Nu6QvX7HDMgaLSjsnYZEnx8IJA',
    'secret': 'jdP302v02pPYRvhzr7CUtmXNOgyEc6V3K4FyJ8mOPsSQOQ8cvDGWHA37viU4Ta5U',
    'timeout': 30000,
    'enableRateLimit': True,
})

fee = .00075
cash = [100, 'USDT']
delay = 5
wallet = 'wallet.csv'

markets = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'BCH/USDT', 'LTC/USDT', 'BNB/USDT', 'ETH/BTC', 'XRP/BTC'
            , 'BNB/BTC', 'LTC/BTC', 'BCH/BTC', 'BTC/BUSD', 'BNB/BUSD', 'XRP/BUSD', 'ETH/BUSD']

coins = ['BTC', 'ETH', 'XRP', 'BCH', 'LTC', 'BNB', 'USDT', 'BUSD']


def options(market):
    optList = []
    for m in markets:
        if market == m:
            continue 
        elif market[0:3] in m:
            optList.append(m)
    return optList

def Reverse(lst): 
    new_lst = lst[::-1] 
    return new_lst 

def triangles():
    paths = []
    for market in markets:

        if market[market.index('/')+1:] != cash[1]:
            continue

        if market[market.index('/')+1:] == 'BTC':
            continue
        optsList = options(market)
        for opt in optsList:
            path = []
            path.append(market)
            path.append(opt)
            if path[1][market.index('/')+1:] == 'BTC':
                opts = options(opt)
                for o in opts:
                    longPath =  path[:]
                    longPath.append(o)
                    if longPath[0][0:3] == longPath[1][0:3] == longPath[2][0:3]:
                        ind = longPath[2].index('/')
                        longPath[2] = f'BTC{longPath[2][ind:]}'
                    paths.append(longPath)
                continue
            paths.append(path)
    revs = []
    for p in paths:
        rev = (Reverse(p))
        if rev[0][rev[0].index('/')+1:] == cash[0]:
            revs.append(rev)
    return paths+revs


def retrieve(market):
    orderbook = exchange.fetch_order_book (market)
    bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
    ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
    spread = (ask - bid) if (bid and ask) else None
    return np.array([bid, ask, spread])

def retrievePrice():
    p = Pool()
    result = p.map(retrieve, markets)
    p.close()
    p.join()
    return np.array(result)

    
def find_discreps(): 
    prices = retrievePrice()
    paths = triangles()
    discreps = []
    for path in paths:
        discrep = []
        c = cash[:]
        i = 0
        for m in path:
            #print(f'market {m}')
            f = fee*c[0]
            #print(f'fee {f} {c[1]}')
            a = prices[markets.index(m)][0]
            #print(f'ask {a}')
            b = prices[markets.index(m)][1]
            #print(f'bid {b}')
            if m == path[0]:
                #print(f'buying ({c[0]}-{f})/{a}')
                c[0] = (c[0]-f)/a
                c[1] = m[0:3]
                #print(f'{c[1]} {c[0]}')
            elif m[0:3] == path[i-1][0:3]:
                #print(f'selling ({c[0]}-{f})*{b}')
                c[0] = (c[0]-f)*b
                c[1] = m[m.index('/')+1:]
                #print(f'{c[1]} {c[0]}')
            elif i == 2:
                #print(f'selling ({c[0]}-{f})*{b}')
                c[0] = (c[0]-f)*b
                c[1] = m[m.index('/')+1:]
                #print(f'{c[1]} {c[0]}')
            else:
                #print(f'buying ({c[0]}-{f})/{a}')
                c[0] = (c[0]-f)/a
                c[1] = m[0:3]
                #print(f'{c[1]} {c[0]}')
            i += 1
        discrep.append(c[0]-cash[0])
        discrep.append(c)
        discrep.append(path)
        discreps.append(discrep)
        #print(f'cash: {c[0]} \ndiscrep: {c[0]-cash[0]}')
        #print('\n')
    return discreps


def newDiscrepTrack():
    d = find_discreps()
    with open('discrepTracker.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(d)

def writeDiscreps():
    newDiscrepTrack()
    while True:
        d = find_discreps()
        with open('discrepTracker.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(d)
        time.sleep(60)
        

def newWallet():
    now = datetime.now()
    time_now = now.strftime('%H:%M:%S')
    with open(wallet, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Coin', 'Cash'])
        writer.writerow([time_now, cash[1], cash[0]])

def simulate():
    global cash
    newWallet()
    try:
        while True:
            start = time.time()

            print('\n')
            d = find_discreps()
            maxDiscrep = 0
            maxCash = cash
            maxPath = []
            for dis in d:
                if dis[0] > maxDiscrep:
                    maxDiscrep = dis[0]
                    maxCash = dis[1]
                    maxPath = dis[2]

            print(f'max discrep {maxDiscrep}')
            print(f'path {maxPath}')
            cash = maxCash
            print(f'cash {cash}')
            
            now = datetime.now()
            time_now = now.strftime('%H:%M:%S')
            with open(wallet, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([time_now, cash[1], cash[0]])

            print(f'{time.time()-start} seconds')

            time.sleep(delay)
    except KeyboardInterrupt:
        print('No longer calculating discrepancies.')




if __name__ == "__main__":
    #cd Documents/GitHub/CryptoArbitrage/
    #start = time.time()
    #print(triangles())
    print(simulate())
    #print(time.time()-start)
    