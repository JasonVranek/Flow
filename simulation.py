from trader import Trader
from order_book import OrderBook
from exchange import Exchange
from graph import Graph

import sys

import random
from matplotlib import pyplot
import numpy as np
import time

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



def main():
	num_orders = 50
	if len(sys.argv) > 1:
		num_orders = int(sys.argv[1])
	print(num_orders)
	# Create the exchange
	ex = Exchange('DEX', 'address', 1_000)

	# Create the order book
	book = test_book()

	# Add the order book to the exchange
	ex.add_book(book)

	# Create the graph object
	graph = Graph()
	graph.exchange = ex

	send_orders(num_orders, ex)

	ex.book.pretty_book()

	ex.hold_batch()

	graph.graph_average_aggregates()

	graph.graph_all_aggregates()




if __name__ == '__main__':
	main()