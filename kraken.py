import ccxt

import numpy as np 
import time
from datetime import datetime
import csv

from multiprocessing import Pool

start = time.time()

kraken = ccxt.kraken()
kraken.apiKey = 'X3upiXJYDR1PXrCkM68xT137ITlI6NBkGC5YmPTtScMVUTz7tysXOlmU'
kraken.secret = 'DLc9U1wcWVcwFSogEqu6B+eSp/mxnATu/4geBc11O3mvoxDPlh1wfkvKBqEF1dm7sjD9/mmfkf5gg4j1ATbVsQ=='


fee = .00075
cash = [100, 'USDT']
delay = 30
wallet = 'wallet.csv'

fm = kraken.fetch_markets()
markets = []
for m in fm:
    markets.append(m['symbol'])

for m in markets:
    if '.d' in m:
        markets.remove(m)


def options(market):
    optList = []
    for m in markets:
        if market == m:
            continue 
        elif market.split('/')[0] in m:
            optList.append(m)
    return optList

def endOptions(path):
    optList = []
    c1 = path[-2].split('/')[0]
    c2 = path[-1].split('/')[0]
    c3 = path[-1].split('/')[1]
    for m in path:
        if c1 == c2 and f'{c3}/USDT' == m:
            optList.append(m)
        elif f'{c2}/USDT' == m:
            optList.append(m)
    return optList

def Reverse(lst): 
    new_lst = lst[::-1] 
    return new_lst 

paths = []
for m in markets:
    if m.split('/')[1] != cash[1]:
        continue
    optsList = options(m)
    for opt in optsList:
        path = []
        path.append(m)
        path.append(opt)
        paths.append(path)

def layers(pList):
    tempPaths = []
    unfinished = []
    for p in pList:
        if '/'+p[0].split('/')[1] in p[-1]:
            continue
        elif len(p) == 2:
            opts = endOptions(p)
            if len(opts) == 0:
                print('p')
            for o in opts:
                path = p[:]
                path.append(o)
                tempPaths.append(path)
        else:
            opts = options(p[-1]) 
            for o in opts:
                path = p[:]
                path.append(o)
                unfinished.append(path)
    global paths
    paths = tempPaths
    if len(unfinished) == 0:
        return
    else:
        layers(unfinished)

layers(paths)

revs = []
for p in paths:
    rev = (Reverse(p))
    if rev[0][rev[0].index('/')+1:] == cash[0]:
        revs.append(rev)

paths = paths+revs

def retrieve(market):
    orderbook = kraken.fetch_order_book(market)
    bid = np.array(orderbook['bids'])
    ask = np.array(orderbook['asks'])
    bidMax = np.amax(bid[:,0])
    askMin = np.amin(ask[:,0])
    return np.array([bidMax, askMin])

def retrievePrice():
    p = Pool()
    result = p.map(retrieve, markets)
    p.close()
    p.join()
    return np.array(result)

def find_discreps(): 
    prices = retrievePrice()
    discreps = []
    for path in paths:
        discrep = []
        c = cash[:]
        i = 0
        for m in path:
            print(f'market {m}')
            f = fee*c[0]
            print(f'fee {f} {c[1]}')
            a = prices[markets.index(m)][0]
            print(f'ask {a}')
            b = prices[markets.index(m)][1]
            print(f'bid {b}')
            if m == path[0]:
                print(f'buying ({c[0]}-{f})/{a}')
                c[0] = (c[0]-f)/a
                c[1] = m.split('/')[0]
                print(f'{c[1]} {c[0]}')
            elif m.split('/')[0] == path[i-1].split('/')[0]:
                print(f'selling ({c[0]}-{f})*{b}')
                c[0] = (c[0]-f)*b
                c[1] = m[m.index('/')+1:]
                print(f'{c[1]} {c[0]}')
            elif path.index(m) == path[-1]:
                print(f'selling ({c[0]}-{f})*{b}')
                c[0] = (c[0]-f)*b
                c[1] = m[m.index('/')+1:]
                print(f'{c[1]} {c[0]}')
            else:
                print(f'buying ({c[0]}-{f})/{a}')
                c[0] = (c[0]-f)/a
                c[1] = m.split('/')[0]
                print(f'{c[1]} {c[0]}')
            i += 1
        discrep.append(c[0]-cash[0])
        discrep.append(c)
        discrep.append(path)
        discreps.append(discrep)
        print(f'cash: {c[0]} \ndiscrep: {c[0]-cash[0]}')
        print('\n')
    return discreps


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
            maxDiscrep = 0.0
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
    print(paths)
    print(time.time()-start)