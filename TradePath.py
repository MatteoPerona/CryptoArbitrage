import time
import ccxt
from numpy import amax, amin, array
from pandas import read_csv
from datetime import datetime
import csv
from multiprocessing import Pool


####################################### Exchange Info ############################################
exchange_id = ['binanceus']
exchange_class = getattr(ccxt, exchange_id[0])
exchange = exchange_class({
	'apiKey': '2ZQ7FNs5snKyFfdCaCm5YjFORnlvtvh46hrK2RjN1SM2LTZ1A3iBo7PfJqcUrtm7',
	'secret': 'qWB1yPCPS3rNeNtScVK06ub7IgBk3wDbsPV94OMkfeBTaX7HVc3pZxKwqNlFXlpt',
	'timeout': 30000,
	'enableRateLimit': True,
})

#Updates the price of BNB to get a better estimate of value of wallet
BNBPrice = 15.5
def updateBNB():   #.5seconds
	global BNBPrice
	BNBPrice = exchange.fetch_ticker('BNB/USD')['bid']


#Fetches the best path from wallet.csv
blacklist = []
path = ['None', 'None']
def updatePath(num, first=False):   #.001seconds
	global path
	try:
		df = read_csv('paths.csv')
	except:
		df = read_csv('pathsBackup.csv')
	if first == False:
		if df.loc[num, 'Discrepancy'] <= 0:
			return None
	string = df.loc[num, 'Path']
	m1 = string.split(',')[0][2:-1]
	m2 = string.split(',')[1][2:-2]
	path = [m1, m2]
	for p in blacklist:
		if p == path:
			print(f'same: {p}, {path}')
			updatePath(num+1, first=True)
			return None
	print(f'path: {path}')

#Trading Settings
fee = .00075
cash = 10.001
delay = 1
currentDiscrep = 0



####################################### Data Collection ############################################
#Fetches orderbook data for given market
def retrievePrices(path):  #1 sec
	prices = []
	for market in path:
		orderbook = exchange.fetch_order_book(market)
		bids = array(orderbook['bids'])[:,0]
		asks = array(orderbook['asks'])[:,0]
		bidMax = amax(bids)
		askMin = amin(asks) 
		prices.append(array([bidMax, askMin]))
	return array(prices)


#################################### Discrepancy Calculations ######################################
start = time.time()
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
def calculateDiscrepancy(path, c):
	prices = retrievePrices(path)
	volume = 0
	for x in range(len(path)):
		price = prices[x]
		if isSell(path, path[x]):
			c = simSell(price[0], c)
		else:
			volume = c/price[1]
			c = simBuy(price[1], c)
	return [c-cash, volume]


############################################# Trading #############################################
currentSymbol = None

#Buy/Sell Commands to abstractify api 
def buy(symbol, ammount):
	print(f'buying: {symbol} {ammount}')
	exchange.create_market_buy_order(symbol, ammount)
def sell(symbol, ammount):
	print(f'selling: {symbol} {ammount}')
	exchange.create_market_sell_order(symbol, ammount)

#True if the given symbol is open: order is not filled, false if the order was filled
def isOpen(symbol=currentSymbol):  #.6 sec
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
def balance():  #.7 sec 
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
def writeBalance():  #.7 sec
	totalBalance = balance()[0]
	now = datetime.now()
	time = now.strftime('%H:%M:%S')
	date = now.strftime('%d-%m-%y')
	with open('balance.csv', 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([date, time, totalBalance, path, currentDiscrep])
		print([date, time, totalBalance])

#looks into balance.csv and determines whether last trade was proffitable
def wasProffitable():
	df = read_csv('balance.csv')
	balance = df['totalBalance'].tail(2)
	last_two_balances = []
	for b in balance:
		last_two_balances.append(b)
	print(last_two_balances)
	if last_two_balances[0] > last_two_balances[1]:
		return False
	return True

#Main buy sell logic
go = False
down = 0 
def main(c):
	global go
	global down
	global currentDiscrep
	discrepancy = calculateDiscrepancy(path, c)
	currentDiscrep = discrepancy[0]
	print(currentDiscrep)
	if currentDiscrep < .001:
		return None
	go = True
	vol = discrepancy[1]
	try:
		buy(path[0], vol)
	except Exception as e:
		print(e)
		go = False
		same = True
		base = path[0].split('/')[1]
		down = 0
		while same:
			down+=1
			oldPath = path
			updatePath(down)
			if path == oldPath:
				same = False
			elif path[0].split('/')[1] != base:
				same = False
		return None
	try:
		sell(path[1], vol)
	except:
		bought = False
		while bought == False:
			try:
				sell(path[1], vol)
				bought = True
			except Exception as e:
				print(e)
				time.sleep(.1)

	print(time.time()-start)


#loops the main method indefinitely
def loop():
	global go
	global down
	global blacklist
	try:
		i = 0
		#updateBNB()
		writeBalance()
		while True:
			i += 1
			print('\n')
			print(f'index: {i}, down:{down}')
			updatePath(down, first=True)
			main(cash)
			if go == True:
				writeBalance()
				if wasProffitable():
					print('proffitable')
					print('sleeping 3 seconds...')
					time.sleep(3)
				else:
					print(f'blacklisting {path}')
					blacklist.append(path)
					print(blacklist)
				go = False
				down = 0
			if i == 10:
				down = 0
				i = 0
	except KeyboardInterrupt:
		print('ending...')
		#cancel()


if __name__ == '__main__':
	loop()
	#buy('BNB/USD', 0.44)
	#sell('BTC/USD', 0.00170572)
	#updateBNB()
	print(balance())
	#writeBalance()
	#updatePath(0, True)
	#print(path)
	#main(cash)
	#writeBalance()
	#sell('BTC/USD', 0.00170213)
	'''
	if wasProffitable():
		print('proffitable')
	else:
		print('no')	
	'''
	











