from trader import Trader
from order_book import OrderBook
from exchange import Exchange
from graph import Graph

import sys

import random
import numpy as np
import time
import string
from threading import Thread

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
		self.html = ''

	def start(self, graph):
		# Start a thread that will always process messages
		t = Thread(target=self.book.process_messages)
		t.daemon = True
		t.start()

		t = Thread(target=self.rand_trader_behavior)
		t.daemon = True
		t.start()

		# Start a thread that will recursively hold batches
		# t = Thread(target=self.run_batch)
		# t.daemon = True
		# t.start()

	def run_batch(self, graph=False):
		# Sleep thread until batch 
		# timeout = Exchange._batch_time
		# time.sleep(timeout)

		self.exchange.hold_batch()

		if graph:
			return self.make_graph()

		# recursively call run_batch after
		# self.run_batch()
		
	def rand_trader_behavior(self):
		while True:
			if random.randint(0, 100) == 1:
				num_traders = random.randint(0, 5)
				print(f'Sending {num_traders} new orders!')
				traders = []
				traders = self.setup_rand_traders(num_traders)
				self.submit_traders_orders(traders)
				time.sleep(1)

			# Send random cancels
			if random.randint(0, 100) == 2:
				num_traders = random.randint(0, 5)
				print(f'Cancelling {num_traders} orders!')
				for x in range(0, num_traders):
					self.cancel_trader(random.choice(self.traders))
				time.sleep(1)

		# Send random updates


	def make_graph(self):
		self.graph.graph_aggregates()
		self.graph.display()
		self.html = self.graph.graph_as_html()
		return self.html

	def setup_rand_trader(self):
		name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
		balance = random.randint(0, 10000)
		trader = Trader(name, balance)
		trader.enter_order(random.choice(['bid', 'ask']), 	# 'bid', 'ask'
							random.randint(101, 200), 		# p_high
							random.randint(10, 100),  		# p_low
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

	sim.exchange.book.temp_process_messages()
	
	html = sim.run_batch(True)

	# if g:
	# 	html = sim.make_graph()

	return html

def setup_simulation(num_orders):
	sim = Simulation('DEX', '0xADDR', 1000, 'ETH', 'DAI')

	# Create num_orders number of random traders 
	sim.setup_rand_traders(num_orders)

	return sim

def run_simulation(num_orders, g):
	sim = setup_simulation(num_orders)

	sim.start(g)

	sim.submit_all_orders()

	# The graphing must happen on the main thread
	while(True):
		# Send random new traders
		html = sim.run_batch(g)

		time.sleep(Exchange._batch_time)

		# sim.graph.close()
		sim.graph.redraw()



def main():
	num_orders = 50
	g = True
	if len(sys.argv) > 1:
		num_orders = int(sys.argv[1])
	
	if len(sys.argv) > 2:	
		if sys.argv[2] == 'f':
			g = False

	print(single_random_graph(num_orders, g))

	# run_simulation(num_orders, g)












if __name__ == '__main__':
	main()