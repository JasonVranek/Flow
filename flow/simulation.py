import sys

from util.profiler import prof
from util.rand_distributions import RandDists as rd
from trader import Trader
from order_book import OrderBook
from exchange import Exchange
from graph import Graph

import random
import numpy as np
import time
import string
import threading
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
		self.clearing_price = np.random.uniform(100)

	def start(self):
		print(f'Starting simulation @{str(datetime.datetime.now())}')
		self.book.pretty_book()

		self.process_flag = threading.Event()
		# Start a thread that will always process messages
		t1 = threading.Thread(target=self.process_forever, args=[self.process_flag])
		# t1 = threading.Thread(target=self.process_forever, args=(self.batch_event, ))
		t1.daemon = True
		t1.start()

		# Start a thead that sends random traders ever batch
		t2 = threading.Thread(target=self.rand_trader_behavior)
		t2.daemon = True
		t2.start()

		self.process_flag.set()

		if self.display_graph:
		# Start the animation loop which triggers the batches
			self.animation_loop()
		# If no graphic is desired run the batch on timer
		else:
			self.batch_loop()

	def animation_loop(self):
		# Make the animation loop run a new batch 
		self.graph.animate(self.run_batch)

	def batch_loop(self):
		self.run_batch(1)
		# self.clearing_price = self.exchange.clearing_price
		time.sleep(self.exchange._batch_time)
		self.batch_loop()

	def run_batch(self, i):
		self.get_batch_time()

		# Clear the process flag in prep for batch which blocks the process_forever thread
		self.process_flag.clear()

		bid_shares_owed, ask_shares_owed = self.exchange.hold_batch()

		# After the batch is run, done the event to resume processing messages
		self.process_flag.set()

		# if self.display_graph:
			# Update the graph
		self.graph.graph_aggregates()
		self.html = self.graph.graph_as_html()
		self.write_html()

		self.pay_traders(bid_shares_owed, ask_shares_owed)

	def pay_traders(self, b_shares, a_shares):
		for o_id in b_shares:
			contents = b_shares[o_id]
			shares_to_add = contents['shares'] 
			p = contents['p*']
			trader = self.traders[self.get_trader(o_id)]
			print('Bid Before ')
			trader.describe()
			# A bidder adds shares of markets base currency and subtracts shares of markets desired currency
			trader.balance += shares_to_add 
			trader.funds -= shares_to_add * p
			print('Bid After ')
			trader.describe()
		for o_id in a_shares:
			contents = a_shares[o_id]
			shares_to_add = contents['shares'] 
			p = contents['p*']
			trader = self.traders[self.get_trader(o_id)]
			print('Ask Before ')
			trader.describe()
			# An asker adds shares of markets base currency and subtracts shares of markets desired currency
			trader.balance += shares_to_add 
			trader.funds -= shares_to_add * p
			print('Ask After ')
			trader.describe()

	def get_trader(self, order_id):
		for x in range(0, len(self.traders)):
			if self.traders[x].account == order_id:
				# return self.traders[x]
				return x

	def write_html(self):
		# Write html to a file for flask to display
		with open('../html/market.html', 'w') as file:
			file.write(self.html)

	def process_forever(self, event):
		while True:
			# Block when until the process_flag is set
			self.process_flag.wait()
			# print(f'Resuming message processing @ {str(datetime.datetime.now())}')
			while self.process_flag.is_set():
				self.book.process_messages()

			# Stop processing if the flag is cleared (during a batch)
			# print(f'Pausing message processing @ {str(datetime.datetime.now())}')

	def rand_trader_behavior(self):
		while True:
			print('New orders:')
			# Cancel from current traders
			try:
				num_traders = rd.num_arrivals(self.exchange._batch_time, beta=.005)
				# print(f'Cancelling {num_traders} orders!')
				for x in range(0, num_traders):
					self.cancel_trader(np.random.choice(self.traders))
			except ValueError:
				print('Tried to cancel but not enough traders in book')
				pass

			# Updates for current traders
			try:
				num_traders = rd.num_arrivals(self.exchange._batch_time, beta=.005)
				# print(f'Cancelling {num_traders} orders!')
				for x in range(0, num_traders):
					self.update_trader(np.random.choice(self.traders))
			except ValueError:
				print('Tried to update but failed')
				pass

			# Send in new traders
			num_traders = rd.num_arrivals(self.exchange._batch_time, beta=.01)
			# print(f'Sending {num_traders} new orders!')
			traders = []
			traders = self.setup_rand_traders(num_traders)
			self.submit_traders_orders(traders)

			# Sleep after sending til batch is over
			time.sleep(self.exchange._batch_time)

	def setup_rand_trader(self):
		name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
		funds = rd.trader_funds(1000)
		trader = Trader(name, funds)
		bid_or_ask = rd.rand_trader_type()
		p_low, p_high = rd.rand_prices(self.clearing_price, bid_or_ask)
		trader.enter_order(bid_or_ask, 				# 'bid', 'ask'
							p_high, 				# p_high
							p_low,  				# p_low
							rd.rand_u_max(10), 		# u_max
							rd.rand_q_max(100))		# q_max
		self.traders.append(trader)
		return trader

	def cancel_trader(self, trader):
		trader.cancel_order()
		# print(f'CANCEL @{str(datetime.datetime.now())}: {trader.current_order}')
		self.exchange.get_order(trader.current_order)
		self.traders.remove(trader)

	def update_trader(self, trader):
		# Update centered around current p*
		p_low, p_high = rd.rand_prices(self.exchange.clearing_price, trader.current_order['trader_type'])
		update = [p_high, 					# p_high
					p_low,  				# p_low
					rd.rand_u_max(10), 		# u_max
					rd.rand_q_max(100)]
		trader.update_order(*update)
		# print(f'UPDATE @{str(datetime.datetime.now())}: {trader.current_order}')
		self.exchange.get_order(trader.current_order)

	def setup_rand_traders(self, n):
		traders = []
		for x in range(0, n):
			traders.append(self.setup_rand_trader())

		return traders

	def submit_traders_orders(self, traders):
		for trader in traders:
			# print(f'ENTER @{str(datetime.datetime.now())}: {trader.current_order}')
			self.exchange.get_order(trader.current_order)

	def submit_all_orders(self):
		for trader in self.traders:
			self.exchange.get_order(trader.current_order)

	def get_batch_time(self):
		t = str(datetime.datetime.now())
		print()
		print(f'Holding Batch: {self.exchange.batch_num} @ {t}')
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
	# single_random_graph(num_orders, g)

	sim = run_simulation(g)










if __name__ == '__main__':
	main()