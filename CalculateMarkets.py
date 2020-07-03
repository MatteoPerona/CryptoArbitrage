import ccxt
import numpy as np


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


def main():
    global markets
    global paths

    #max length of a path
    longestPath = 2

    #Currencies that can be used interchangeably when calculating discrepancies
    #Currencies that can end chains of trades
    stableCurrencies = ['USD', 'USDT', 'BUSD']

    #retrieves all tickest from exchange and initalizes markets list
    markets = []
    tickers = exchange.fetch_tickers()

    #finds all base currencies in exchange and appends them so a list
    baseCurrencies = []
    for value in tickers.values():
        base = value['symbol'].split('/')[1]
        if len(baseCurrencies) == 0:
            baseCurrencies.append(base)
        count = 0
        for baseCurrency in baseCurrencies:
            if baseCurrency == base:
                break
            else:
                count += 1
        if count == len(baseCurrencies):
            baseCurrencies.append(base)

    #Groups markets by base currency and appends most liqud markets to markets list
    for currency in baseCurrencies:
        symbols = []
        volumes = []
        for value in tickers.values():
            ticker      = value['symbol']
            base        = ticker.split('/')[1]
            quoteVolume = value['quoteVolume']
            if base == currency:
                symbols.append(ticker)
                volumes.append(quoteVolume)
        average = np.mean(np.array(volumes))
        removes = []
        for x in range(len(volumes)):
            if volumes[x] < average:
                removes.append(symbols[x])
        for remove in removes:
            for symbol in symbols:
                if remove == symbol:
                    symbols.remove(symbol)
                    break
        for symbol in symbols:
            markets.append(symbol)

    #Removes any dead end markets
    for market in markets:
        top   = market.split('/')[0]
        count = 0
        for m in markets:
            if market == m:
                count += 1
                continue
            t = m.split('/')[0]
            b = m.split('/')[1]
            if top == t or top == b:
                break
            else:
                count += 1
        if count == len(markets):
            markets.remove(market)

    #Removes stable currency markets ***This could be taken out if logic is adjusted***
    for market in markets:
        for currency in stableCurrencies:
            if market.split('/')[0] == currency:
                markets.remove(market)
                break

    #Makes a list of markets that can start or end a path
    terminalMarkets = []
    for market in markets:
        base = market.split('/')[1]
        for c in stableCurrencies:
            if c == base:
                terminalMarkets.append(market)
                break

    #Returns true if the inputted coin can be used to purchse on the inputted market
    def buyable(c, m):
        b = m.split('/')[1]
        if c == b:
            return True
        return False

    #Returns true if the inputted coin can be used to sold on the inputted market
    def sellable(c, m):
        t = m.split('/')[0]
        if c == t:
            return True
        return False

    #Returns a list of the markets that work with the inputted market
    def findOptions(coin, market):
        options  = []
        for m in markets:
            if market == m:
                continue
            elif sellable(coin, m):
                options.append(m)
            elif buyable(coin, m):
                options.append(m)
        return options

    #Returns true if the given market is a terminalMarket
    def isTerminalMarket(m):
        for market in terminalMarkets:
            if m == market:
                return True
        return False

    #Returns true if the last step was buy and false if the next step is sell
    def isBuy(path):
        last    = path[-1]
        lastTop = last.split('/')[0]
        prev    = path[-2]
        prevTop = prev.split('/')[0]
        if lastTop == prevTop:
            return False
        return True

    #Returns a list of all possible paths up to the given length
    paths = []
    for market in terminalMarkets:
        options = findOptions(market.split('/')[0], market)
        for option in options:
            path = [market]
            path.append(option)
            paths.append(path)

    def findPaths(maxLen=2, maxLenConstant=2):
        global paths
        if maxLen <= 2:
            removes = []
            for path in paths:
                if not isTerminalMarket(path[-1]):
                    removes.append(path)
            for remove in removes:
                i = paths.index(remove)
                paths.remove(paths[i])
            return None
        newPaths = []
        for path in paths:
            if isTerminalMarket(path[-1]):
                continue
            elif isBuy(path):
                options = findOptions(path[-1].split('/')[0], path[-1])
                for option in options:
                    newPath = path[:]
                    newPath.append(option)
                    newPaths.append(newPath)
                paths.remove(path)
            else:
                options = findOptions(path[-1].split('/')[1], path[-1])
                for option in options:
                    newPath = path[:]
                    newPath.append(option)
                    newPaths.append(newPath)
                paths.remove(path)
        #print(f'\n{maxLenConstant-maxLen+1}')
        #for path in newPaths:
            #print(path)
        paths += newPaths
        findPaths(maxLen-1, maxLenConstant)
    findPaths(longestPath, longestPath)

if __name__=="__main__":
    main()
    #print(markets)
    for path in paths:
        print(path )