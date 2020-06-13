import ccxt
import CryptoArb

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

currentSymbol = 'BNB/USDT'

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


def main():
    print('\n')
    top = CryptoArb.top()
    path = top[0]
    price = top[1]
    discrep = top[2]
    cash = CryptoArb.cash
    for x in range(len(path)):
        currentSymbol = path[x]
        f = CryptoArb.fee*price[x]
        if x == 0:
            #exchange.create_limit_buy_order(path[x], cash[0], price[x])
            print(f'exchange.create_limit_buy_order({path[x]}, {cash[0]}, {price[x]})')
            cash[1] = path[x].split('/')[0]

        elif path[x].split('/')[0] == path[x-1].split('/')[0]:
            #exchange.create_limit_sell_order(path[x], cash[0], price[x])
            print(f'exchange.create_limit_sell_order({path[x]}, {cash[0]}, {price[x]})')
            cash[1] = path[x].split('/')[1]

        elif x == 2:
            #exchange.create_limit_sell_order(path[x], cash[0], price[x])
            print(f'exchange.create_limit_sell_order({path[x]}, {cash[0]}, {price[x]})')
            cash[1] = path[x].split('/')[1]

        else:
            #exchange.create_limit_buy_order(path[x], cash[0], price[x])
            print(f'exchange.create_limit_buy_order({path[x]}, {cash[0]}, {price[x]})')
            cash[1] = path[x].split('/')[0]

        cash[0] = discrep+cash[0]
        
        while isOpen(path[x]):
            time.sleep(1)
        print('\n')

    CryptoArb.cash = cash


def loop():
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print('ending...')
        cancel()
        
        

        
#exchange.create_limit_buy_order (symbol, amount, price[, params])
#exchange.create_limit_sell_order (symbol, amount, price[, params])

if __name__ == "__main__":
    #print(exchange.requiredCredentials)
    start = time.time()

    #main()
    loop()

    #cancel()
    
    print(time.time()-start)
