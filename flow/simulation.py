from trader import Trader
from order_book import OrderBook
from exchange import Exchange
from graph import Graph

import sys

import random
import numpy as np
import time
import string

from profiler import prof

class Simulation(object):
	def __init__(self, name, addr, balance, base_cur, desired_cur):
		self.name = name
		self.exchange = Exchange(name, addr, balance)
		self.book = OrderBook(base_cur, desired_cur)
		self.exchange.book = self.book	
		self.graph = Graph()
		self.graph.exchange = self.exchange	
		self.traders = []

	def start(self):
		pass
		# Always process messages

		# Always receive new messages

		# Hold a batch auction every batch_time

	def setup_rand_trader(self):
		name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
		balance = random.randint(0, 10000)
		trader = Trader(name, balance)
		trader.enter_order(random.choice(['bid', 'ask']), 	# 'bid', 'ask'
							random.randint(101, 120), 		# p_high
							random.randint(80, 99),  		# p_low
							random.randint(400, 500), 		# u_max
							random.randint(1000, 2000))		# q_max
		self.traders.append(trader)
		return trader

	def setup_trader(self, name, balance, order):
		trader = Trader(name, balance)
		trader.enter_order(*order)
		self.traders.append(trader)
		return trader

	def cancel_trader(self, trader):
		trader.cancel_order()
		self.exchange.get_order(trader.current_order)

	def update_trader(self, trader, update):
		trader.update_order(*update)

	def setup_rand_traders(self, n):
		traders = []
		for x in range(0, n):
			traders.append(self.setup_rand_trader())

		return traders

	def submit_traders_orders(self, traders):
		for trader in traders:
			self.exchange.get_order(trader.current_order)

	def submit_all_orders(self):
		for trader in self.traders:
			self.exchange.get_order(trader.current_order)

def single_random_graph(num_orders, g=True):
	# Setup the simulation
	sim = Simulation('DEX', '0xADDR', 1000, 'ETH', 'DAI')

	# Create num_orders number of random traders 
	sim.setup_rand_traders(num_orders)

	# Submit all of the orders into the book
	sim.submit_all_orders()

	sim.exchange.book.process_messages()
	
	sim.exchange.hold_batch()

	if g:
		sim.graph.test_graph()
		sim.graph.display()
		html = sim.graph.graph_as_html()

	return html

def main():
	num_orders = 50
	g = True
	if len(sys.argv) > 1:
		num_orders = int(sys.argv[1])
	
	if len(sys.argv) > 2:	
		if sys.argv[2] == 'f':
			g = False

	print(single_random_graph(num_orders, g))













if __name__ == '__main__':
	main()