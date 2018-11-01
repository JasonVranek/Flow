from trader import Trader
from order_book import OrderBook
from exchange import Exchange
from graph import Graph

import sys

import random
from matplotlib import pyplot
import numpy as np
import time

from profiler import prof



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
	print(f'Creating {num_traders} new traders and sending orders:')
	for i in range(0, num_traders):
		name = f'Trader{i}'
		trader = Trader(name, random.randint(50, 300))
		trader.new_order(random.choice(order_type), 		# 'buy', 'sell'
							random.randint(101, 120), 		# p_high
							random.randint(80, 99),  		# p_low
							random.randint(400, 500), 		# u_max
							random.randint(1000, 2000))		# q_max
		traders.append(trader)
		# print(trader.current_order)
	return traders

def send_orders(num_orders, exchange):
	# Create new trader trader
	traders = setup_traders(num_orders)

	# Send an order to the exchange's order book
	for trader in traders:
		exchange.get_order(trader.current_order)

	print('Received:', len(exchange.book.message_queue), 'messages')

	# Process any messages in the book's queue
	while len(exchange.book.message_queue) > 0:
		exchange.book.process_messages()

	return traders

def send_cancels(traders, exchange):
	for trader in traders:
		if random.randint(0, 1):
		# if trader.current_order['order_type'] == 'sell':
			# Test only cancelling bids
			trader.new_order('C', None, None, None, None)
			exchange.get_order(trader.current_order)

	# Process any messages in the book's queue
	while len(exchange.book.message_queue) > 0:
		exchange.book.process_messages()

def test_cancels():
	ex = Exchange('DEX', 'address', 1_000)

	# Create the order book
	book = test_book()

	# Add the order book to the exchange
	ex.add_book(book)

	# Create the graph object
	graph = Graph()
	graph.exchange = ex

	n = 10
	bidders = []
	askers = []
	# Create the N traders with bids
	for x in range(0, n):
		bidders.append(Trader(f'bidder {x}'))
		bidders[x].new_order('buy', 
							(x + 1) * 100,	 # p_high
							80,				 # p_low
							1000,			 # u_max
							2000)			 # q_max
		ex.get_order(bidders[x].current_order)

	# Create the N traders with asks and send to exchange
	for x in range(0, n):
		askers.append(Trader(f'asker {x}'))
		askers[x].new_order('sell', 
							(x + 1) * 100,	 # p_high
							80,				 # p_low
							1000,			 # u_max
							2000)			 # q_max
		ex.get_order(askers[x].current_order)

	# Process any messages in the book's queue
	while len(ex.book.message_queue) > 0:
		ex.book.process_messages()

	ex.book.pretty_book()

	# Hold the batch
	ex.hold_batch()

	print(ex.aggregate_demand, ex.aggregate_supply)

	# Graph the 
	graph.graph_total_aggregates(1, 'r', 'b', 'g-')
	graph.graph_all_aggregates(2, 'r', 'b')

	print(ex.active_bids, ex.active_asks)

	# Send cancels for the odd orders
	for x in range(0, n):
		if x % 2 == 1:
			bidders[x].new_order('C', None, None, None, None)
			ex.get_order(bidders[x].current_order)

	# Create the N traders with asks and send to exchange
	for x in range(0, n):
		if x % 2 == 1:
			askers[x].new_order('C', None, None, None, None)
			ex.get_order(askers[x].current_order)

	# Process any messages in the book's queue
	while len(ex.book.message_queue) > 0:
		ex.book.process_messages()

	ex.book.pretty_book()

	# Hold the batch
	ex.hold_batch()

	print(ex.aggregate_demand, ex.aggregate_supply)

	# Confirm that those were the ones deleted
	graph.graph_total_aggregates(3, 'r', 'b', 'g-')
	graph.graph_all_aggregates(4, 'r', 'b')

	graph.display()

def test_updates(num_orders):
	# Create the exchange
	ex = Exchange('DEX', 'address', 1_000)

	# Create the order book
	book = test_book()

	# Add the order book to the exchange
	ex.add_book(book)

	# Create the graph object
	graph = Graph()
	graph.exchange = ex

	traders = send_orders(num_orders, ex)

	ex.book.pretty_book()

	ex.hold_batch()

	graph.graph_total_aggregates(1, 'r', 'b', 'g-')
	graph.graph_all_aggregates(2, 'r', 'b')

	for trader in traders:
		trader.new_order(random.choice(['buy', 'sell']), 		# 'buy', 'sell'
							random.randint(101, 120), 		# p_high
							random.randint(80, 99),  		# p_low
							random.randint(400, 500), 		# u_max
							random.randint(1000, 2000))		# q_max
		# trader.new_order('sell', 		# 'buy', 'sell'
		# 					105, 		# p_high
		# 					70,  		# p_low
		# 					400, 		# u_max
		# 					1000)		# q_max
		ex.get_order(trader.current_order)

	while len(ex.book.message_queue) > 0:
		ex.book.process_messages()

	ex.book.pretty_book()

	ex.hold_batch()

	graph.graph_total_aggregates(3, 'pink', 'cyan', 'g-')
	graph.graph_all_aggregates(4, 'pink', 'cyan')

	print(ex.active_asks, ex.active_bids)

	graph.display()	

# @prof
def test_resize(g=True):
	#Create the exchange
	ex = Exchange('DEX', 'address', 1_000)

	# Create the order book
	book = test_book()

	# Add the order book to the exchange
	ex.add_book(book)

	# Create the graph object
	graph = Graph()
	graph.exchange = ex

	# Create 10 traders
	n = 10
	bidders = []
	askers = []
	# Create the N traders with bids
	for x in range(0, n):
		bidders.append(Trader(f'bidder {x}'))
		bidders[x].new_order('buy', 
							(x + 1) * 100,	 # p_high
							80,				 # p_low
							1000,			 # u_max
							2000)			 # q_max
		ex.get_order(bidders[x].current_order)

	# Create the N traders with asks and send to exchange
	for x in range(0, n):
		askers.append(Trader(f'asker {x}'))
		askers[x].new_order('sell', 
							(x + 1) * 100,	 # p_high
							80,				 # p_low
							1000,			 # u_max
							2000)			 # q_max
		ex.get_order(askers[x].current_order)

	# Process any messages in the book's queue
	while len(ex.book.message_queue) > 0:
		ex.book.process_messages()

	ex.book.pretty_book()

	# Hold the batch
	ex.hold_batch()

	# Graph the default schedules, p_high = 1000
	if g:
		graph.graph_all_aggregates(1, 'r', 'b')
		graph.graph_total_aggregates(2, 'r', 'b', 'g-')

	# Create a new trader with a p_high double max_price
	big_bidder = Trader('Big Bidder')
	big_bidder.new_order('buy', 2000, 80, 1000, 2000)
	ex.get_order(big_bidder.current_order)

	# Process the new message
	while len(ex.book.message_queue) > 0:
		ex.book.process_messages()

	ex.book.pretty_book()

	# Hold the batch
	ex.hold_batch()

	if g:
		graph.graph_all_aggregates(3, 'r', 'b')
		graph.graph_total_aggregates(4, 'r', 'b', 'g-')

	# Cancel the order with a high p_high
	# big_bidder.new_order('C', None, None, None, None)
	big_bidder.new_order('buy', 1500, 80, 1000, 2000)
	ex.get_order(big_bidder.current_order)

	# Process the new message
	while len(ex.book.message_queue) > 0:
		ex.book.process_messages()

	ex.book.pretty_book()

	# Hold the batch
	ex.hold_batch()

	if g:
		graph.graph_all_aggregates(5, 'r', 'b')
		graph.graph_total_aggregates(6, 'r', 'b', 'g-')
		graph.display()

# @prof
def test_random(num_orders, g=True):
	# Create the exchange
	ex = Exchange('DEX', 'address', 1_000)

	# Create the order book
	book = test_book()

	# Add the order book to the exchange
	ex.add_book(book)

	# Create the graph object
	graph = Graph()
	graph.exchange = ex

	traders = send_orders(num_orders, ex)

	# ex.book.pretty_book()

	ex.hold_batch()

	if g:
		graph.graph_total_aggregates(1, 'r', 'b', 'g-')
		# graph.graph_all_aggregates(2, 'r', 'b')

		graph.display()


def main():
	num_orders = 50
	g = True
	if len(sys.argv) > 2:
		num_orders = int(sys.argv[1])
		if sys.argv[2] == 'f':
			g = False
	
	test_random(num_orders, g)
	# test_updates(num_orders)
	# test_cancels()
	# test_resize(g=False)











if __name__ == '__main__':
	main()