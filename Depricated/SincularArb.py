import ccxt
import numpy as np 
import pandas as pd
import time
from datetime import datetime
import csv


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

path = ['BTC/BUSD', 'BTC/USDT']

BNBPrice = 16
def updateBNB():
	global BNBPrice
	BNBPrice = exchange.fetch_ticker('BNB/USD') 


def updatePath():
	global path
	df = pd.read_csv('wallet.csv')
	string = df.tail(1)['Path'].item()
	m1 = string.split(',')[0][2:-1]
	m2 = string.split(',')[1][2:-2]
	path = [m1, m2]
	print(f'\n{path}')


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
	prices = []
	for market in iter:
		prices.append(retrieve(market))
	return prices 
	#p = Pool()
	#result = p.map(retrieve, iter)
	#p.close()
	#p.join()
	#return np.array(result)


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
currentCurrency = 'BUSD'

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
				if key == 'BUSD' or key == 'USDT':
					total += value
				elif key == 'BNB':
					value *= BNBPrice
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
		print([date, time, totalBalance])

#Buy/Sell Commands to abstractify api 
def buy(symbol, ammount, price):
	#exchange.create_limit_buy_order(symbol, ammount, price)
	exchange.create_market_buy_order(symbol, ammount)

def sell(symbol, ammount, price):
	#exchange.create_limirt_sell_order(symbol, ammount, price)
	exchange.create_market_sell_order(symbol, ammount)

#Handles logic of buying and selling given discrepancy information and cash volume
def main(cash):
	global currentSymbol
	global currentCurrency
	discrepancy = calculateDiscrepancy(path)
	print(f'{discrepancy}')
	if path[0].split('/')[0] == 'BTC':
		if discrepancy[0] < 0.003:
			return None
	else:
		if discrepancy[0] < 0.01:
			return None
	writeBalance()
	prices = discrepancy[1]
	for x in range(len(path)):
		if isSell(path, path[x]):
			print(f'selling: {vol} {path[x]} at {prices[x]}')
			try:
				sell(path[x], vol, prices[x])
			except:
				time.sleep(1)
				sell(path[x], vol, prices[x])
			cash = vol*prices[x]
			cash -= cash*fee
			currentCurrency = path[x].split('/')[1]
			writeBalance()
		else:
			vol = cash/prices[x]
			print(f'buying: {vol} {path[x]} at {prices[x]}')
			buy(path[x], vol, prices[x])
			vol -= vol*fee
			currentCurrency = path[x].split('/')[0]
		currentSymbol = path[x]
		print(currentSymbol)
		retries = 0
		while isOpen(currentSymbol):
			retries+=1
			time.sleep(.25*retries)
			if retries == 20:
				if x == 0:
					pass
					#print('canceling..')
					#cancel(currentSymbol)
					#time.sleep(5)
					#return None
				else :
					return None

consecDiscreps = 0
def main2(cash):
	global currentSymbol
	global currentCurrency
	global consecDiscreps
	discrepancy = calculateDiscrepancy(path)
	print(f'{discrepancy}')
	if discrepancy[0] < 0.0001:
		consecDiscreps = 0 
		return None
	else:
		consecDiscreps += 1
		if consecDiscreps <= 1:
			return None
		else:
			consecDiscreps = 0 
	writeBalance()
	prices = discrepancy[1]
	for x in range(len(path)):
		if isSell(path, path[x]):
			print(f'selling: {vol} {path[x]} at {prices[x]}')
			try:
				sell(path[x], vol, prices[x])
			except:
				time.sleep(1)
				sell(path[x], vol, prices[x])
			cash = vol*prices[x]
			cash -= cash*fee
			currentCurrency = path[x].split('/')[1]
			writeBalance()
		else:
			vol = cash/prices[x]
			print(f'buying: {vol} {path[x]} at {prices[x]}')
			buy(path[x], vol, prices[x])
			vol -= vol*fee
			currentCurrency = path[x].split('/')[0]
		currentSymbol = path[x]
		print(currentSymbol)
		retries = 0
		while isOpen(currentSymbol):
			retries+=1
			time.sleep(.25*retries)
			if retries == 20:
				if x == 0:
					pass
					#print('canceling..')
					#cancel(currentSymbol)
					#time.sleep(5)
					#return None
				else :
					return None


#loops the main method indefinitely
def loop():
	updateBNB()
	try:
		while True:
			updatePath()
			try:
				main2(10.05)
			except:
				try:
					exchange.create_market_buy_order('BUSD/USD', 10.05)
					time.sleep(2)
				except:
					exchange.create_market_sell_order('USDT/USD', 10.05)
					time.sleep(1)
					exchange.create_market_buy_order('BUSD/USD', 10.05)
					time.sleep(2)
			time.sleep(1)
	except KeyboardInterrupt:
		print('ending...')
		cancel()


############################################# Debuging #############################################
if __name__ == "__main__":
	start = time.time()

	#main(10.05)
	loop()
	#updatePath()
	#updateBNB()
	#print(balance())
	#sell('ZIL/USD', 605.3, 0.0199)
	#exchange.create_market_sell_order('USDT/USD', 10.3)
	#exchange.create_market_buy_order('BUSD/USD', 10)
	#exchange.create_market_sell_order('BTC/BUSD', 0.00107696)
	#exchange.create_market_sell_order('ZIL/BUSD', 483.7988)
	#writeBalance()
	#cancel('BTC/BUSD')
	#isOpen('BTC/BUSD')


	print(time.time()-start)
