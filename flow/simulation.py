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
import math



class Simulation(object):
	def __init__(self, name, addr, balance, base_cur, desired_cur):
		self.name = name
		self.exchange = Exchange(name, addr, balance)
		self.book = OrderBook(base_cur, desired_cur)
		self.exchange.book = self.book	
		self.graph = Graph(self.exchange)
		self.traders = {}
		self.html = ''
		self.display_graph = False
		self.clearing_price = np.random.uniform(20, 50)
		self.first_time = True

	def start(self):
		print(f'Starting simulation @{str(datetime.datetime.now())}')
		self.book.pretty_book()

		self.process_flag = threading.Event()
		# Start a thread that will always process messages
		t1 = threading.Thread(target=self.process_forever, args=[self.process_flag])
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
		# Sleep after initiating the batch process until the next batch
		time.sleep(self.exchange._batch_time)
		self.batch_loop()

	def run_batch(self, i):
		# Print out the batch's start time
		self.get_batch_time()

		# Clear the process flag in prep for batch which blocks the process_forever thread
		self.process_flag.clear()

		# Hold the batch and get back the payout dictionaries
		bid_shares_owed, ask_shares_owed = self.exchange.hold_batch()

		# After the batch is run, set the event to resume processing messages
		self.process_flag.set()

		# Graph the outcome of the batch and write it to html file
		self.graph.graph_aggregates()
		self.html = self.graph.graph_as_html()
		self.write_html()

		# Pay the traders based on the clearing price
		self.pay_traders(bid_shares_owed, ask_shares_owed)

	def pay_traders(self, b_shares, a_shares):
		sum_to_askers = 0
		sum_from_askers = 0
		sum_to_bidders = 0
		sum_from_bidders = 0
		# Iterate over the payout dictionary and update each trader's balance and funds
		for o_id in b_shares:
			# Get the trader's owed shares from dictionary
			contents = b_shares[o_id]
			if contents['shares'] == 0:
				continue
			# Get the trader from the dictionary of all traders
			trader = self.traders[o_id]

			# A bidder adds shares to balance and subtracts shares*clearing_price from funds
			f_before = trader.funds
			b_before = trader.balance
			trader.balance += contents['shares']
			trader.funds -= contents['shares']   * contents['p*'] 

			sum_to_bidders += contents['shares'] 
			sum_from_bidders -= contents['shares']   * contents['p*'] 

			print(f'Bidder {o_id}: balance {b_before}->{trader.balance}, funds {f_before}->{trader.funds}')
			if trader.funds <= 0:
				print('Cancelling trader')
				trader.describe()
				self.cancel_trader(trader)
				print()
		print()
		for o_id in a_shares:
			contents = a_shares[o_id]
			if contents['shares'] == 0:
				continue
			# Get the trader from the dictionary of all traders
			trader = self.traders[o_id]

			# An asker adds shares to balance and subtracts shares/clearing_price from funds
			f_before = trader.funds
			b_before = trader.balance
			trader.balance += contents['shares'] * contents['p*'] 
			trader.funds -= contents['shares']  
			sum_to_askers += contents['shares'] * contents['p*'] 
			sum_from_askers -= contents['shares']  

			print(f'Asker {o_id}: balance {b_before}->{trader.balance}, funds {f_before}->{trader.funds}')
			if trader.funds <= 0:
				print('Cancelling trader')
				trader.describe()
				self.cancel_trader(trader)
				print()

		print(f'Amount bidders paid: {sum_from_bidders}, received: {sum_to_bidders}')
		print(f'Amount askers paid: {sum_from_askers}, received: {sum_to_askers}')

		self.update_funds_in_book()

	def update_funds_in_book(self):
		for o_id, order in self.book.bids.items():
			try:
				trader = self.traders[o_id]
				order['funds'] = trader.funds
			except KeyError:
				print(f'KeyError updating {o_id} funds')
				continue

		for o_id, order in self.book.asks.items():
			try:
				trader = self.traders[o_id]
				order['funds'] = trader.funds
			except KeyError:
				print(f'KeyError updating {o_id} funds')
				continue

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
			# try:
			# 	num_traders = rd.num_arrivals(self.exchange._batch_time, beta=.001)
			# 	# print(f'Cancelling {num_traders} orders!')
			# 	for x in range(0, num_traders):
			# 		trader_id = np.random.choice(list(self.traders))
			# 		self.cancel_trader(self.traders[trader_id])
			# except ValueError:
			# 	print('Tried to cancel but not enough traders in book')
			# 	pass

			# Updates for current traders
			try:
				num_traders = rd.num_arrivals(self.exchange._batch_time, beta=.005)
				# print(f'Updating {num_traders} orders!')
				for x in range(0, num_traders):
					trader_id = np.random.choice(list(self.traders))
					self.update_trader(self.traders[trader_id])
			except ValueError:
				print('Tried to update but failed')
				pass

			# Send in new traders
			if self.first_time:
				self.first_time = False
				# num_traders = rd.num_arrivals(self.exchange._batch_time, beta=.01)
				num_traders = math.ceil(np.random.uniform(20, 50))
				print(f'Sending {num_traders} new orders!')
				traders = []
				traders = self.setup_rand_traders(num_traders)
				self.submit_traders_orders(traders)

			# Sleep after sending til batch is over
			time.sleep(self.exchange._batch_time)

	def setup_rand_trader(self):
		name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
		bid_or_ask = rd.rand_trader_type()
		funds = rd.trader_funds(self.clearing_price, bid_or_ask)
		trader = Trader(name, funds)
		p_low, p_high = rd.rand_prices(self.clearing_price, bid_or_ask)
		trader.enter_order(bid_or_ask, 				# 'bid', 'ask'
							p_high, 				# p_high
							p_low,  				# p_low
							rd.rand_u_max(10), 		# u_max
							rd.rand_q_max(100))		# q_max
		self.traders[name] = trader
		return trader

	def cancel_trader(self, trader):
		trader.cancel_order()
		# print(f'CANCEL @{str(datetime.datetime.now())}: {trader.current_order}')
		self.exchange.get_order(trader.current_order)
		self.traders.pop(trader.account)

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