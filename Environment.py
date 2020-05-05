import Data
import time 
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

'''simulates buying and selling cryptos, tracking data through csv files'''
'''make a csv that tracks ownership and worth of each coin owned'''

wallet = 'wallet.csv'

fees = 0
tradeDelay = 0

def buy(coin):
    with open(wallet, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ticker, 'Data'])

def sell(coin):
    with open(wallet, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ticker, 'Data'])

def plotGrowth():
    

if if __name__ == "__main__":
    print(pd.read_csv(wallet))