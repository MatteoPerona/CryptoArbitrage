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
	#'apiKey': 'sbne6lN7qdZDoj4bSGiL368N81sOQnf37bPvb9Nu6QvX7HDMgaLSjsnYZEnx8IJA',
	#'secret': 'jdP302v02pPYRvhzr7CUtmXNOgyEc6V3K4FyJ8mOPsSQOQ8cvDGWHA37viU4Ta5U',
	'apiKey': '2ZQ7FNs5snKyFfdCaCm5YjFORnlvtvh46hrK2RjN1SM2LTZ1A3iBo7PfJqcUrtm7',
	'secret': 'qWB1yPCPS3rNeNtScVK06ub7IgBk3wDbsPV94OMkfeBTaX7HVc3pZxKwqNlFXlpt',
	'timeout': 30000,
	'enableRateLimit': True,
})

paths = [['BTC/USD', 'BTC/USDT'], ['BTC/USDT', 'BTC/USD'], ['BTC/BUSD', 'BTC/USDT'], ['BTC/USDT', 'BTC/BUSD']]

################################### Simulations Settings #########################################
fee = .00075
cash = 10
delay = 1
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
def retrievePrices(iter):
	p = Pool()
	result = p.map(retrieve, iter)
	p.close()
	p.join()
	return np.array(result)


#################################### Discrepancy Calculations ######################################
def calcFee(capital):
	return capital*fee

def simBuy(price, volume):
	f = calcFee(volume/price)
	return volume/price-f

def simSell(price, volume):
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

#Same as calculateDiscrepancies but it works with one specified path instead of all paths
def calculateDiscrepancy(path):
	prices = retrievePrices(path)
	c = cash
	pricePerUnit = []
	for x in range(len(path)):
		price = prices[x]
		if isSell(path, path[x]):
			c = simSell(price[0], c)
			pricePerUnit.append(price[0])
		else:
			c = simBuy(price[1], c)
			pricePerUnit.append(price[1])
	return [c-cash, pricePerUnit]


############################################# Trading #############################################
currentSymbol = 'BTC/USD'
currentCurrency = 'USDT'

#True if the given symbol is open: order is not filled, false if the order was filled
def isOpen(symbol=currentSymbol):
	openOrders = exchange.fetch_open_orders(symbol)
	if len(openOrders) == 0:
		print('order filled!')
		return False
	else:
		print('not yet filled...')
		return True

#Cancels an open order with the given symbol
def cancel(symbol=currentSymbol):
	openOrder = exchange.fetch_open_orders(symbol)
	orderId = openOrder[0]['info']['orderId']
	exchange.cancel_order(orderId, symbol)

#Retruns total dollar value of binance account and a list of assets with their USD volumes
def balance():
	balance = exchange.fetch_balance()
	total = 0
	individualTotals = []
	for key in balance.keys():
		try:
			value = balance[key]['total']
			if key == 'USD':
				total += value
				individualTotals.append([key, value])
			elif value > 0:
				price = exchange.fetch_ticker(f'{key}/USD')['bid']
				value *= price
				total += value
				individualTotals.append([key, value])
		except:
			continue
	return [total, individualTotals]

#adds the current date, time, and binance account balance to balance.csv
def writeBalance():
	totalBalance = balance()[0]
	now = datetime.now()
	time = now.strftime('%H:%M:%S')
	date = now.strftime('%d-%m-%y')
	with open('balance.csv', 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([date, time, totalBalance])

#Buy/Sell Commands to abstractify api 
def buy(symbol, ammount, price):
	exchange.create_limit_buy_order(symbol, ammount, price)
def sell(symbol, ammount, price):
	exchange.create_limit_sell_order(symbol, ammount, price)

#Handles logic of buying and selling given discrepancy information and cash volume
def main(cash):
	start = time.time()
	global currentSymbol
	global currentCurrency
	if currentCurrency == 'USD':
		pathNum = 0
	else:
		pathNum = 1
	discrepancy = calculateDiscrepancy(paths[pathNum])
	print(discrepancy)
	if discrepancy[0] < 0:
		return None
	path = paths[pathNum]
	prices = discrepancy[1]

	for x in range(len(path)):
		currentSymbol = path[x]
		if isSell(path, path[x]):
			print(f'selling: {vol} {path[x]} at {prices[x]}')
			sell(path[x], vol, prices[x])
			cash = vol*prices[x]
			cash -= cash*fee
			currentCurrency = path[x].split('/')[1]
		else:
			vol = cash/prices[x]
			print(f'buying: {vol} {path[x]} at {prices[x]}')
			buy(path[x], vol, prices[x])
			vol -= vol*fee
			currentCurrency = path[x].split('/')[0]
		time.sleep(.25)
		while isOpen():
			time.sleep(.25)
	print(f'cash: {cash} {currentCurrency}')
	print(time.time()-start)

def loop():
	try:
		while True:
			main(11)
			writeBalance()
			time.sleep(5)
	except KeyboardInterrupt:
		print('ending...')
		cancel() 

############################################# Debuging #############################################
if __name__ == "__main__":
	start = time.time()

	#main(11)
	loop()
	#print(balance())

	print(time.time()-start)
