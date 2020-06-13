import ccxt
import numpy as np 
import time
from datetime import datetime
import csv
from multiprocessing import Pool

#Exchange
exchange_id = ['binanceus']
exchange_class = getattr(ccxt, exchange_id[0])
exchange = exchange_class({
    #'apiKey': 'sbne6lN7qdZDoj4bSGiL368N81sOQnf37bPvb9Nu6QvX7HDMgaLSjsnYZEnx8IJA',
    #'secret': 'jdP302v02pPYRvhzr7CUtmXNOgyEc6V3K4FyJ8mOPsSQOQ8cvDGWHA37viU4Ta5U',
    'apiKey': '2ZQ7FNs5snKyFfdCaCm5YjFORnlvtvh46hrK2RjN1SM2LTZ1A3iBo7PfJqcUrtm7',
    'secret': 'qWB1yPCPS3rNeNtScVK06ub7IgBk3wDbsPV94OMkfeBTaX7HVc3pZxKwqNlFXlpt',
    'timeout': 30000,
    'enableRateLimit': True,
})


#Simulations Settings
fee = .00075
cash = 10
delay = 1
wallet = 'wallet.csv'


#Path Finding
symbols = exchange.fetch_symbols()
print(symbols)

#Data Collection


#Discrepancy Calculations


#Data Packaging and Exporting 
