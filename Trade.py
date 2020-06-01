import ccxt
import CryptoArb

import time

exchange_id = 'binanceus'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': 'sbne6lN7qdZDoj4bSGiL368N81sOQnf37bPvb9Nu6QvX7HDMgaLSjsnYZEnx8IJA',
    'secret': 'jdP302v02pPYRvhzr7CUtmXNOgyEc6V3K4FyJ8mOPsSQOQ8cvDGWHA37viU4Ta5U',
    'timeout': 30000,
    'enableRateLimit': True,
})

def main():
    print('\n')
    top = CryptoArb.top()
    path = top[0]
    price = top[1]
    cash = 10###############need actual cash amount 
    for x in range(len(path)):
        if x == 0:
            print(f'exchange.create_limit_buy_order({path[x]}, {cash}, {price[x]})')
            print('\n')
        elif path[x].split('/')[0] == path[x-1].split('/')[0]:
            print(f'exchange.create_limit_sell_order({path[x]}, {cash}, {price[x]})')
            print('\n')
        elif x == 2:
            print(f'exchange.create_limit_sell_order({path[x]}, {cash}, {price[x]})')
            print('\n')
        else:
            print(f'exchange.create_limit_buy_order({path[x]}, {cash}, {price[x]})')
            print('\n')
        
        
        

        
#exchange.create_limit_buy_order (symbol, amount, price[, params])
#exchange.create_limit_sell_order (symbol, amount, price[, params])

if __name__ == "__main__":
    print(exchange.requiredCredentials)
    start = time.time()
    main()
    print(time.time()-start)
