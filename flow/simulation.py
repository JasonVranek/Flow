import sys

from util.profiler import prof
from trader import Trader
from order_book import OrderBook
from exchange import Exchange
from graph import Graph

import random
import numpy as np
import time
import string
from threading import Thread
import datetime



class Simulation(object):
	def __init__(self, name, addr, balance, base_cur, desired_cur):
		self.name = name
		self.exchange = Exchange(name, addr, balance)
		self.book = OrderBook(base_cur, desired_cur)
		self.exchange.book = self.book	
		self.graph = Graph(self.exchange)
		self.traders = []
		self.html = ''
		self.display_graph = False

	def start(self):
		print(f'Starting simulation @{str(datetime.datetime.now())}')
		self.book.pretty_book()

		# Start a thread that will always process messages
		t = Thread(target=self.process_forever)
		t.daemon = True
		t.start()

		# Start a thead that sends random traders ever batch
		t = Thread(target=self.rand_trader_behavior)
		t.daemon = True
		t.start()

		# Start the animation loop which triggers the batches

		if self.display_graph:
			self.animation_loop()

		else:
			self.batch_loop()

	def animation_loop(self):
		# Make the animation loop run a new batch 
		self.graph.animate(self.run_batch)

	def batch_loop(self):
		self.run_batch(1)
		time.sleep(self.exchange._batch_time)
		self.batch_loop()

	def run_batch(self, i):
		self.get_batch_time()

		self.exchange.hold_batch()

		# if self.display_graph:
			# Update the graph
		self.graph.graph_aggregates()
		self.html = self.graph.graph_as_html()
		self.write_html()

	def write_html(self):
		with open('../html/market.html', 'w') as file:
			file.write(self.html)

	def process_forever(self):
		while True:
			self.book.process_messages()

	def gen_rand_num(self, beta=.002):
		#tau is the batch length
		tau = self.exchange._batch_time * 1000

		# beta is expected wait time for traders to arrive
		# beta = (1 / 200) 

		# lambda is the intensity param
		lam = beta * tau

		n = np.random.poisson(int(lam))

		return n

	def get_html(self):
		html = self.html
		return html
		
	def rand_trader_behavior(self):
		while True:
			print('New orders:')
			# Cancel from current traders
			try:
				num_traders = self.gen_rand_num(beta=.005)
				# print(f'Cancelling {num_traders} orders!')
				for x in range(0, num_traders):
					self.cancel_trader(np.random.choice(self.traders))
			except ValueError:
				print('Tried to cancel but not enough traders in book')
				pass

			# Updates for current traders
			try:
				num_traders = self.gen_rand_num(beta=.005)
				# print(f'Cancelling {num_traders} orders!')
				for x in range(0, num_traders):
					self.update_trader(np.random.choice(self.traders))
			except ValueError:
				print('Tried to update but failed')
				pass

			# Send in new traders
			num_traders = self.gen_rand_num(beta=.01)
			# print(f'Sending {num_traders} new orders!')
			traders = []
			traders = self.setup_rand_traders(num_traders)
			self.submit_traders_orders(traders)

			# Sleep after sending til batch is over
			time.sleep(self.exchange._batch_time)

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
		print(f'CANCEL @{str(datetime.datetime.now())}: {trader.current_order}')
		self.exchange.get_order(trader.current_order)
		self.traders.remove(trader)

	def update_trader(self, trader):
		#update = [p_high, p_low, u_max, q_max]
		update = [np.random.randint(101, 200), 		# p_high
					np.random.randint(10, 100),  		# p_low
					np.random.randint(400, 500), 		# u_max
					np.random.randint(1000, 2000)]
		trader.update_order(*update)
		print(f'UPDATE @{str(datetime.datetime.now())}: {trader.current_order}')
		self.exchange.get_order(trader.current_order)

	def setup_rand_traders(self, n):
		traders = []
		for x in range(0, n):
			traders.append(self.setup_rand_trader())

		return traders

	def submit_traders_orders(self, traders):
		for trader in traders:
			print(f'ENTER @{str(datetime.datetime.now())}: {trader.current_order}')
			self.exchange.get_order(trader.current_order)

	def submit_all_orders(self):
		for trader in self.traders:
			self.exchange.get_order(trader.current_order)

	def get_batch_time(self):
		t = str(datetime.datetime.now())
		print()
		# print(f'Holding Batch: {self.exchange.batch_num} @ {t}')
		return t

# @prof
def single_random_graph(num_orders, g=True):
	# Setup the simulation
	sim = Simulation('DEX', '0xADDR', 1000, 'ETH', 'DAI')

	sim.display_graph = g

	# Create num_orders number of random traders 
	sim.setup_rand_traders(num_orders)

	# Submit all of the orders into the book
	sim.submit_all_orders()

	sim.exchange.book.process_messages()
	
	html = sim.run_batch(1)

	if g:
		sim.graph.display()

	html = sim.html

	return html

def setup_simulation(g):
	sim = Simulation('DEX', '0xADDR', 1000, 'ETH', 'DAI')
	sim.display_graph = g
	return sim

def run_simulation(g):
	sim = setup_simulation(g)

	sim.start()

	return sim

def main():
	num_orders = 50
	g = True
	if len(sys.argv) > 1:
		num_orders = int(sys.argv[1])
	
	if len(sys.argv) > 2:	
		if sys.argv[2] == 'f':
			g = False

	# print(single_random_graph(num_orders, g))

	sim = run_simulation(g)










if __name__ == '__main__':
	main()