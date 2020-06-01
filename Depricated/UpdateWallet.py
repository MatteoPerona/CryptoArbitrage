import FindTriangles as ab

import pandas as pd
import csv

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from datetime import datetime
import time



cash = 100
fee = .00075
lag = 15
wallet = 'wallet.csv'
data = pd.read_csv('usdtbtc.csv')



#Modular Functions
def high():
    max = 0
    min = 0
    maxCol = 'ETH/BTC'
    minCol = 'ETH/BTC'
    row = data.tail(1)
    if max==0 and min==0:
        max = row['ETH/BTC'].item()
        min = row['ETH/BTC'].item()
    for column in row:
        if row[column].item()>max:
            max = row[column].item()
            maxCol = column
        elif row[column].item()<min:
            min = row[column].item()
            minCol = column
    if max<abs(min):
        return [minCol, min]  
    return [maxCol, max]


def newWallet():
    with open(wallet, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Coin', 'Cash'])
        writer.writerow([datetime.now(), 'none', cash])


def arbitrage():
    with open(wallet, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), high()[0], (cash/ab.lastTrade(high()[0])['price']*abs(high()[1])).item()])


def main():
    newWallet()
    try:
        while True:
            arbitrage()
    except KeyboardInterrupt:
        print('KeyboadrdInterrupt: No longer updating wallet.csv')


#Fixed Functions
def plotWallet():
    plt.style.use('fivethirtyeight')
    df = pd.read_csv(wallet)
    df.plot(x='Time', y='Cash')
    plt.show()


def testingHigh(x):
    max = 0
    min = 0
    maxCol = 'ETH/BTC'
    minCol = 'ETH/BTC'
    row = data[x:x+1]
    if max==0 and min==0:
        max = row['ETH/BTC'].item()
        min = row['ETH/BTC'].item()
    for column in row:
        if row[column].item()>max:
            max = row[column].item()
            maxCol = column
        elif row[column].item()<min:
            min = row[column].item()
            minCol = column
    if max<abs(min):
        return [minCol, min]  
    return [maxCol, max]


def tArb(x):
    for i in range(x):
        with open(wallet, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now(), testingHigh(i)[0], (cash/ab.lastTrade(testingHigh(i)[0])['price']*abs(testingHigh(i)[1])).item()])



if __name__ == "__main__":
    #fixed tests
    '''newWallet()
    tArb(700)
    plotWallet()
    arbitrage()'''
    
    #Updating Data
    main()

    
    
    