'''''import ccxt
#import Arbitrage
import time

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

currentSymbol = 'BTC/USD'

def isOpen(symbol=currentSymbol):
    openOrders = exchange.fetch_open_orders(symbol)
    if len(openOrders) == 0:
        print('order filled!')
        return False
    else:
        print('not yet filled...')
        return True

def cancel(symbol=currentSymbol):
    openOrder = exchange.fetch_open_orders(symbol)
    orderId = openOrder[0]['info']['orderId']
    exchange.cancel_order(orderId, symbol)


def main(cash):
    top = Arbitrage.topDiscrepancy()
    discrep = top[0]
    print(discrep)
    if discrep < 0:
        return None
    path = top[1]
    print(path)
    prices = top[2]
    print(prices)
    for x in range(len(path)):
        currentSymbol = path[x]
        if x == 0:
            print(f'exchange.create_limit_buy_order({path[x]}, {cash/prices[x]}, {prices[x]})')
            exchange.create_limit_buy_order(path[x], cash/prices[x], prices[x])
        elif path[x].split('/')[0] == path[x-1].split('/')[0]:
            exchange.create_limit_sell_order(path[x], cash/prices[x], prices[x])
            print(f'exchange.create_limit_sell_order({path[x]}, {cash/prices[x]}, {prices[x]})')
        elif x == 2:
            exchange.create_limit_sell_order(path[x], cash/prices[x], prices[x])
            print(f'exchange.create_limit_sell_order({path[x]}, {cash/prices[x]}, {prices[x]})')
        else:
            exchange.create_limit_buy_order(path[x], cash/prices[x], prices[x])
            print(f'exchange.create_limit_buy_order({path[x]}, {cash/prices[x]}, {prices[x]})')
        while isOpen(path[x]):
            #discrep = Atbitrage.calculateDiscrepancy(path)
            if discrep[0] < 0 and x == 0:
                print(discrep[0])
                print('canceling...')
                cancel()
        print('\n')


def loop(delay):
    try:
        while True:
            main(10)
        time.sleep(delay)
    except KeyboardInterrupt:
        print('ending...')
        cancel()
        
        

        
#exchange.create_limit_buy_order (symbol, amount, price[, params])
#exchange.create_limit_sell_order (symbol, amount, price[, params])

if __name__ == "__main__":
    #print(exchange.requiredCredentials)
    start = time.time()

    Arbitrage.reCalculateMarkets()
    main(12)
    #loop(5)
    #exchange.create_market_buy_order('BUSD/USD', 10)
    #isOpen('BUSD/USD')
    #cancel('USDT/USD')

    #print(exchange.fetch_balance())
    
    print(time.time()-start)
'''''