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
import datetime

from profiler import prof

class Simulation(object):
	def __init__(self, name, addr, balance, base_cur, desired_cur):
		self.name = name
		self.exchange = Exchange(name, addr, balance)
		self.book = OrderBook(base_cur, desired_cur)
		self.exchange.book = self.book	
		self.graph = Graph(self.exchange)
		self.traders = []
		self.html = ''

	def start(self, graph):
		# Start a thread that will always process messages
		t = Thread(target=self.process_forever)
		t.daemon = True
		t.start()

		t = Thread(target=self.rand_trader_behavior)
		t.daemon = True
		t.start()

		# Start a thread that will recursively hold batches
		# t = Thread(target=self.run_batch)
		# t.daemon = True
		# t.start()

	def get_batch_time(self):
		t = str(datetime.datetime.now())
		print(f'Holding Batch: self.exchange.batch_num @ {t}')

		return t

	def animation_loop(self):
		# Make the animation loop run a new batch 
		self.graph.animate(self.run_batch)

	def run_batch(self, graph=False):
		# Sleep thread until batch 
		# timeout = Exchange._batch_time
		# time.sleep(timeout)


		print(self.get_batch_time())

		self.exchange.hold_batch()

		# Update the graph
		self.graph.graph_aggregates()

		if graph:
			return self.make_graph()

		# Sleep until the next batch time
		# time.sleep(Exchange._batch_time)

	def process_forever(self):
		while True:
			self.book.process_messages()
		
	def rand_trader_behavior(self):
		while True:
			if np.random.randint(0, 100) == 1:
				num_traders = np.random.randint(0, 5)
				print(f'Sending {num_traders} new orders!')
				traders = []
				traders = self.setup_rand_traders(num_traders)
				self.submit_traders_orders(traders)
				time.sleep(1)

			# Send random cancels
			if np.random.randint(0, 100) == 2:
				num_traders = np.random.randint(0, 5)
				print(f'Cancelling {num_traders} orders!')
				for x in range(0, num_traders):
					self.cancel_trader(np.random.choice(self.traders))
				time.sleep(1)

		# Send random updates


	def make_graph(self):
		# self.graph.redraw()
		# self.graph.graph_aggregates()
		# self.graph.animate()
		# self.graph.display()
		# self.html = self.graph.graph_as_html()
		# return self.html
		return ''

	def setup_rand_trader(self):
		name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
		balance = np.random.uniform(0, 10000)
		trader = Trader(name, balance)
		trader.enter_order(np.random.choice(['bid', 'ask']), 	# 'bid', 'ask'
							np.random.randint(101, 200), 		# p_high
							np.random.randint(10, 100),  		# p_low
							np.random.randint(400, 500), 		# u_max
							np.random.randint(1000, 2000))		# q_max
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

# @prof
def single_random_graph(num_orders, g=True):
	# Setup the simulation
	sim = Simulation('DEX', '0xADDR', 1000, 'ETH', 'DAI')

	# Create num_orders number of random traders 
	sim.setup_rand_traders(num_orders)

	# Submit all of the orders into the book
	sim.submit_all_orders()

	sim.exchange.book.process_messages()
	
	html = sim.run_batch(g)

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

	sim.animation_loop()

	# The graphing must happen on the main thread
	# while(True):
		# Send random new traders
		# html = sim.run_batch(g)

		# time.sleep(Exchange._batch_time)

		# sim.graph.pause()
		# sim.graph.close()
		# sim.graph.redraw()



def main():
	num_orders = 50
	g = True
	if len(sys.argv) > 1:
		num_orders = int(sys.argv[1])
	
	if len(sys.argv) > 2:	
		if sys.argv[2] == 'f':
			g = False

	# single_random_graph(num_orders, g)

	run_simulation(num_orders, g)









if __name__ == '__main__':
	main()