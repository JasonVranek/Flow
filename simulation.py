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
	# order_type = ['buy', 'sell', 'C', 'poop']
	order_type = ['buy', 'sell']
	for i in range(0, num_traders):
		# name = 'Trader' + str(i)
		name = f'Trader{i}'
		trader = Trader(name, random.randint(50, 300))
		trader.new_order(random.choice(order_type), 		# 'buy', 'sell', 'c'
							random.randint(100, 120), 	# p_high
							random.randint(80, 100),  	# p_low
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
	traders = setup_traders(10)

	# Send an order to the exchange's order book
	for trader in traders:
		# ex.book.receive_message(trader.current_order)
		ex.get_order(trader.current_order)

	print('Received:', len(ex.book.message_queue), 'messages')

	# Process any messages in the book's queue
	while len(ex.book.message_queue) > 0:
		ex.book.process_messages()

	ex.book.pretty_book()

	# print('TESTING CANCEL ******************************')
	# for trader in traders:
	# 	trader.new_order('C', None, None, None, None)
	# 	ex.get_order(trader.current_order)

	# while len(ex.book.message_queue) > 0:
	# 	ex.book.process_messages()

	# ex.book.pretty_book()


	# jason = test_trader()
	# ex.get_order(jason.current_order)
	# ex.book.process_messages()
	# ex.book.pretty_book()

	ex.calc_aggregate_demand()
	for x in range(0,1000000):
		pass
	ex.calc_aggregate_supply()
	# print(ex.aggregate_supply)
	# print(ex.aggregate_demand)
	# demand_schedule = ex.calc_demand(jason.current_order)

	# supply_schedule = ex.calc_supply(jason.current_order)
	# print('supply', supply_schedule[:,0])
	# print('price', supply_schedule[:,1])

	# length, u_max = ex.find_longest_schedule(True)
	# print('largest demand', length, u_max)
	# ex.resize_schedules(length, u_max, True)
	# print('largest supply', ex.find_longest_schedule(False))
	ex.book.pretty_book()

	p_low, p_high = ex.get_price_range()
	ex.resize_schedules(p_low, p_high, True)

	# p_low, p_high = ex.get_price_range(False)
	ex.resize_schedules(p_low, p_high, False)


	for ss in ex.aggregate_supply:
		pyplot.plot(ss[1][:,1], ss[1][:,0], 'b')

	for dd in ex.aggregate_demand:
		pyplot.plot(dd[1][:,1], dd[1][:,0], 'r')

	pyplot.show()



if __name__ == '__main__':
	main()