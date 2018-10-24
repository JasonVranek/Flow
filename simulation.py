from trader import Trader
from order_book import OrderBook
from exchange import Exchange

import random
from matplotlib import pyplot
import numpy as np

def test_book():
	book = OrderBook('ETH', 'BTC')
	return book


def test_trader():
	jason = Trader('jasons account', 100)
	order = jason.new_order('buy', 101, 99, 500, 10000)
	# cancel_order = jason.new_order('C', None, None, None, None)
	jason.describe()
	return jason


def setup_traders(num_traders):
	traders = []
	order_type = ['buy', 'sell', 'C', 'poop']
	# order_type = ['buy', 'sell']
	for i in range(0, num_traders):
		# name = 'Trader' + str(i)
		name = f'Trader{i}'
		trader = Trader(name, random.randint(50, 300))
		trader.new_order(random.choice(order_type), 		# 'buy', 'sell', 'c'
							random.randint(100, 110), 	# p_high
							random.randint(90, 100),  	# p_low
							random.randint(0, 500), 		# u_max
							random.randint(1000, 2000))	# q_max
		traders.append(trader)
		print(trader.current_order)
	return traders


def main():
	# Create the exchange
	ex = Exchange('DEX', 'address', 1_000)

	# Create the order book
	book = test_book()

	# Add the order book to the exchange
	ex.add_book(book)

	# Create a new trader
	traders = setup_traders(20)

	# Send an order to the exchange's order book
	for trader in traders:
		# ex.book.receive_message(trader.current_order)
		ex.get_order(trader.current_order)

	print('Received:', len(ex.book.message_queue), 'messages')

	# Process any messages in the book's queue
	while len(ex.book.message_queue) > 0:
		ex.book.process_messages()

	ex.book.pretty_book()

	print('TESTING CANCEL ******************************')
	for trader in traders:
		trader.new_order('C', None, None, None, None)
		ex.get_order(trader.current_order)

	while len(ex.book.message_queue) > 0:
		ex.book.process_messages()

	ex.book.pretty_book()


	jason = test_trader()
	ex.get_order(jason.current_order)
	ex.book.process_messages()
	ex.book.pretty_book()

	demand_schedule = ex.calc_demand(jason.current_order)

	supply_schedule = ex.calc_supply(jason.current_order)
	# print('supply', supply_schedule[:,0])
	# print('price', supply_schedule[:,1])

	pyplot.scatter(supply_schedule[:,1], supply_schedule[:,0])
	pyplot.scatter(demand_schedule[:,1], demand_schedule[:,0])

	pyplot.show()



if __name__ == '__main__':
	main()