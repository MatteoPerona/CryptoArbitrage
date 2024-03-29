import ccxt
import numpy as np 
import time
from datetime import datetime
import csv
from multiprocessing import Pool
import os
import random
import CalculateMarkets

####################################### Exchange Info ############################################
exchange_id = ['binanceus']
exchange_class = getattr(ccxt, exchange_id[0])
exchange = exchange_class({
    'apiKey': 'sbne6lN7qdZDoj4bSGiL368N81sOQnf37bPvb9Nu6QvX7HDMgaLSjsnYZEnx8IJA',
    'secret': 'jdP302v02pPYRvhzr7CUtmXNOgyEc6V3K4FyJ8mOPsSQOQ8cvDGWHA37viU4Ta5U',
    #'apiKey': '2ZQ7FNs5snKyFfdCaCm5YjFORnlvtvh46hrK2RjN1SM2LTZ1A3iBo7PfJqcUrtm7',
    #'secret': 'qWB1yPCPS3rNeNtScVK06ub7IgBk3wDbsPV94OMkfeBTaX7HVc3pZxKwqNlFXlpt',
    'timeout': 30000,
    'enableRateLimit': True,
})

markets = []
paths = []
def reCalculateMarkets():
    global markets
    global paths
    CalculateMarkets.main()
    markets = CalculateMarkets.markets
    paths = CalculateMarkets.paths 


################################### Simulations Settings #########################################
fee = .00075
cash = 10
delay = 5
wallet = 'wallet.csv'


####################################### Data Collection ############################################
#Fetches orderbook data for given market
def retrieve(market):
    orderbook = exchange.fetch_order_book(market)
    bids = np.array(orderbook['bids'])[:,0]
    asks = np.array(orderbook['asks'])[:,0]
    bidMax = np.amax(bids)
    askMin = np.amin(asks) 
    return np.array([bidMax, askMin])

#Maps each market in markets to the retrieve function to be processed in parallel
def retrievePrices(iter=markets):
    p = Pool()
    result = p.map(retrieve, iter)
    p.close()
    p.join()
    return np.array(result)


#################################### Discrepancy Calculations ######################################
def calcFee(capital):
    return capital*fee

def buy(price, volume):
    f = calcFee(volume/price)
    return volume/price-f

def sell(price, volume):
    f = calcFee(volume*price)
    return volume*price-f

#Boolean that returns true if the given market is a sell in the context of the given path
def isSell(path, market):
    index = path.index(market)
    prev  = path[index-1]
    if index == 0:
        return False
    elif market.split('/')[0] == prev.split('/')[0]:
        return True
    return False

#Returns a list = [the amount of money one would gain/lose on a path, the path, and the price at each step of the path]
def calculateDiscrepancies():
    prices = retrievePrices(markets)
    discrepancies = []
    for path in paths:
        c = cash
        pricePerUnit = []
        for x in range(len(path)):
            price = prices[markets.index(path[x])]
            if isSell(path, path[x]):
                c = sell(price[0], c)
                pricePerUnit.append(price[0])
            else:
                c = buy(price[1], c)
                pricePerUnit.append(price[1])
        discrepancy = c-cash
        discrepancies.append([discrepancy, path, pricePerUnit])
    return discrepancies

#Same as calculateDiscrepancies but it works with one specified path instead of all paths
def calculateDiscrepancy(path):
    prices = retrievePrices(path)
    c = cash
    pricePerUnit = []
    for x in range(len(path)):
        price = prices[x]
        if isSell(path, path[x]):
            c = sell(price[0], c)
            pricePerUnit.append(price[0])
        else:
            c = buy(price[1], c)
            pricePerUnit.append(price[1])
    return [c-cash, pricePerUnit]



################################## Data Packaging and Exporting ####################################
#Returns the top discrepancy
def topDiscrepancy(discreps):
    topDiscrep = discreps[0]
    for d in discreps:
        if d[0] > topDiscrep[0]:
            topDiscrep = d
    return topDiscrep

#Simulates the trades by writing data to a csv file  
def simulate():
    reCalculateMarkets()
    now = datetime.now()
    time_now = now.strftime('%H:%M:%S')
    with open(wallet, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Cash', 'Path'])
    global cash
    try:
        while True:
            start = time.time()
            top = topDiscrepancy(calculateDiscrepancies())
            cash = top[0]+cash
            path  = top[1]
            now = datetime.now()
            time_now = now.strftime('%H:%M:%S')
            with open(wallet, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([time_now, cash, path])
            print(f'\n{round(time.time()-start, 2)} seconds')
            print(f'${top[0]}')
            print(f'${cash}')
            print(f'path:{path}')
            time.sleep(delay)
    except KeyboardInterrupt:
        now = datetime.now()
        date = now.strftime('%d-%m-%y')
        try:
            os.rename('./wallet.csv', f'./Depricated/wallet{date}.csv')
        except:
            os.rename('./wallet.csv', f'./Depricated/wallet{date}rand{random.randint(0,20)}.csv')
        print('Ending Simulation')


def best():
    reCalculateMarkets()
    print('starting')
    discreps = calculateDiscrepancies()
    temp = discreps[:]
    with open('pathsBackup.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Discrepancy', 'Path', 'PPU'])
        for x in range(len(discreps)):
            top = topDiscrepancy(temp)
            writer.writerow(top)
            temp.remove(top)
    time.sleep(delay)
    print('done with backup')
    while True:
        try:
            discreps = calculateDiscrepancies()
            temp = discreps[:]
            with open('paths.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Discrepancy', 'Path', 'PPU'])
                for x in range(len(discreps)):
                    top = topDiscrepancy(temp)
                    writer.writerow(top)
                    temp.remove(top)
            time.sleep(delay)
            print('wrote')
        except:
            print('timed out: now sleeping 1800')
            time.sleep(60)
            print('done sleeping')
            continue

    

############################################# Debuging #############################################
if __name__ == "__main__":
    #reCalculateMarkets()

    '''for path in paths:
        print(path)

    prices = retrievePrices()
    for price in prices:
        print(price)'''
    
    '''for market in markets:
        print(market)'''

    '''for discrepancy in calculateDiscrepancies():
        print(discrepancy)'''

    #print(topDiscrepancy())

    #print(calculateDiscrepancy(paths[0]))

    #simulate()

    best()


