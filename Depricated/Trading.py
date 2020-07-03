import Arbitrage as a
import time

exchange = a.exchange
currentSymbol = 'BTC/USD'
currentCurrency = 'USD'

############################################# Interfacing ###########################################
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
					value *= 16
					total += value
				individualTotals.append([key, value])
		except:
			continue
	return [total, individualTotals]

#Creates a new csv file called balance.csv
def newBalanceCSV():
	with open('balance.csv', 'w', newline='') as file:
		writer = a.csv.writer(file)
		writer.writerow(['Date', 'Time', '($) Balance'])

#adds the current date, time, and binance account balance to balance.csv
def writeBalance():
	totalBalance = balance()[0]
	now = a.datetime.now()
	time = now.strftime('%H:%M:%S')
	date = now.strftime('%d-%m-%y')
	with open('balance.csv', 'a', newline='') as file:
		writer = a.csv.writer(file)
		writer.writerow([date, time, totalBalance])


############################################### Logic ###############################################
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
	discrepancy = a.topDiscrepancy()
	print(discrepancy)
	if discrepancy[0] < 0:
		return None
	path   = discrepancy[1]
	prices = discrepancy[2]

	for x in range(len(path)):
		currentSymbol = path[x]
		if a.isSell(path, path[x]):
			print(f'selling: {vol} {path[x]} at {prices[x]}')
			sell(path[x], vol, prices[x])
			cash = vol*prices[x]
			cash -= cash*a.fee
			currentCurrency = path[x].split('/')[1]
		else:
			vol = cash/prices[x]
			print(f'buying: {vol} {path[x]} at {prices[x]}')
			buy(path[x], vol, prices[x])
			vol -= vol*a.fee
			currentCurrency = path[x].split('/')[0]
		time.sleep(.5)
		retries = 0
		while isOpen():
			time.sleep(.5)
			retries += 1
			time.sleep(retries*.5)
			print(retries)
	print(f'cash: {cash} {currentCurrency}')
	print(time.time()-start)

def loop():
	a.reCalculateMarkets()
	try:
		while True:
			main(10)
			print('\n')
			time.sleep(10)
			writeBalance()
	except KeyboardInterrupt:
		print('ending...')
		cancel() 

		


############################################# Debuging #############################################
if __name__ == '__main__':
	#a.reCalculateMarkets()
	#main(11)
	#print('\n\n\n')
	#loop()
	#exchange.create_market_sell_order('USDT/USD', 40)
	#exchange.create_market_buy_order('BUSD/USD', 10)
	#exchange.create_market_sell_order('BNB/BUSD', .8)
	exchange.create_market_sell_order('ZIL/BUSD', 545.8)
	#print(balance())
	#isOpen('BTC/BUSD')
	#cancel('BTC/BUSD')
	#writeBalance()



	