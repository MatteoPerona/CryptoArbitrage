import ccxt

import numpy as np 
import time
from datetime import datetime
import csv

from multiprocessing import Pool


exchange_id = 'binanceus'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    #'apiKey': 'sbne6lN7qdZDoj4bSGiL368N81sOQnf37bPvb9Nu6QvX7HDMgaLSjsnYZEnx8IJA',
    #'secret': 'jdP302v02pPYRvhzr7CUtmXNOgyEc6V3K4FyJ8mOPsSQOQ8cvDGWHA37viU4Ta5U',
    'apiKey': '2ZQ7FNs5snKyFfdCaCm5YjFORnlvtvh46hrK2RjN1SM2LTZ1A3iBo7PfJqcUrtm7',
    'secret': 'qWB1yPCPS3rNeNtScVK06ub7IgBk3wDbsPV94OMkfeBTaX7HVc3pZxKwqNlFXlpt',
    'timeout': 30000,
    'enableRateLimit': True,
})

fee = .000375
cash = [10, 'USDT']
delay = 1
wallet = 'wallet.csv'

markets = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'BCH/USDT', 'LTC/USDT', 'BNB/USDT', 'ETH/BTC', 'XRP/BTC'
            , 'BNB/BTC', 'LTC/BTC', 'BCH/BTC', 'BTC/BUSD', 'BNB/BUSD', 'XRP/BUSD', 'ETH/BUSD']


def options(market):
    optList = []
    for m in markets:
        if market == m:
            continue 
        elif market.split('/')[0] in m:
            optList.append(m)
    return optList

def Reverse(lst): 
    new_lst = lst[::-1] 
    return new_lst 

def triangles():
    paths = []
    for market in markets:

        #if market[market.index('/')+1:] != cash[1]:
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
                    if longPath[0].split('/')[0] == longPath[1].split('/')[0] == longPath[2].split('/')[0]:
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
    bids = np.array(orderbook['bids'])[:,0]
    asks = np.array(orderbook['asks'])[:,0]
    bidMax = np.amax(bids)
    askMin = np.amin(asks)
    spread = askMin-bidMax
    avg = bidMax*askMin/2
    bips = spread/avg
    #print(f'\nMarket: {market}\nBid: {bidMax}\nAsk: {askMin}\nSpread: {spread}\nBibs: {bips}\n')
    arr = np.array([bidMax, askMin, bips])
    #arr = np.array([bidMax+spread*.499, askMin-spread*.499, spread])
    return arr

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
            a = prices[markets.index(m)][1]
            #print(f'ask {a}')
            b = prices[markets.index(m)][0]
            #print(f'bid {b}')
            if m == path[0]:
                #print(f'buying ({c[0]}-{f})/{a}')
                c[0] = (c[0]-c[0]*fee)/a
                c[1] = m.split('/')[0]
                #print(f'{c[1]} {c[0]}')
            elif m.split('/')[0] == path[i-1].split('/')[0]:
                #print(f'selling ({c[0]}-{f})*{b}')
                c[0] = c[0]*b
                c[1] = m[m.index('/')+1:]
                c[0] = c[0]-fee*c[0]
                #print(f'{c[1]} {c[0]}')
            elif path[i] == path[-1]:
                #print(f'selling ({c[0]}-{f})*{b}')
                c[0] = c[0]*b
                c[1] = m[m.index('/')+1:]
                c[0] = c[0]-fee*c[0]
                #print(f'{c[1]} {c[0]}')
            else:
                #print(f'buying ({c[0]}-{f})/{a}')
                c[0] = (c[0]-c[0]*fee)/a
                c[1] = m.split('/')[0]
                #print(f'{c[1]} {c[0]}')
            i += 1
        discrep.append(c[0]-cash[0])
        discrep.append(c)
        discrep.append(path)
        discreps.append(discrep)
        #print(f'cash: {c[0]} \ndiscrep: {c[0]-cash[0]}')
        #print('\n')
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
            #maxDiscrep = 0.0
            maxDiscrep = -100.0
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

def findDiscreps(): 
    prices = retrievePrice()
    paths = triangles()
    discreps = []
    for path in paths:
        discrep = []
        ppu = []
        c = cash[:]
        i = 0
        for m in path:
            a = prices[markets.index(m)][1]
            b = prices[markets.index(m)][0]
            if m == path[0]:
                c[0] = c[0]/a
                c[1] = m.split('/')[0]
                ppu.append(a)
            elif m.split('/')[0] == path[i-1].split('/')[0]:
                c[0] = c[0]*b
                c[1] = m[m.index('/')+1:]
                ppu.append(b)
            elif i == 2:
                c[0] = c[0]*b
                c[1] = m[m.index('/')+1:]
                ppu.append(b)
            else:
                c[0] = c[0]/a
                c[1] = m.split('/')[0]
                ppu.append(a)
            c[0]=c[0]-fee*c[0]
            i += 1
        discrep.append(c[0]-cash[0])
        #print(c[0]-cash[0])
        discrep.append(path)
        discrep.append(ppu)
        discreps.append(discrep)
    return discreps

def top():
    d = findDiscreps()
    maxDiscrep = 0.0
    maxPath = []
    prices = []
    for dis in d:
        if dis[0] > maxDiscrep:
            #print(dis)
            maxDiscrep = dis[0]
            maxPath = dis[1]
            prices = dis[2]
    return [maxPath, prices, maxDiscrep]




if __name__ == "__main__":
    #cd Documents/GitHub/CryptoArbitrage/
    start = time.time()

    #print(retrievePrice())
    #print(triangles())
    #print(find_discreps())
    #print(findDiscreps())
    #print(top())
    simulate()
    
    print(time.time()-start)
    