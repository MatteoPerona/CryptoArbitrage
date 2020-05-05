# coding=utf-8

import ccxt

hitbtc   = ccxt.hitbtc({'verbose': True})
bitmex   = ccxt.bitmex()
huobipro = ccxt.huobipro()
binance = ccxt.binance()

print(binance.id, binance.load_markets)
print(binance.fetch_ticker)
    