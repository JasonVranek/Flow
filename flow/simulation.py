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
		# self.pay_traders(bid_shares_owed, ask_shares_owed)
		self.exchange_funds(bid_shares_owed, ask_shares_owed, self.exchange.clearing_price)

	def exchange_funds(self, bid_shares, ask_shares, p):
		# Get list of trader id's so we can easily pop
		bidders = list(bid_shares)
		askers = list(ask_shares)

		for bid_id in bidders:
			# Get the trader's owed shares from dictionary
			bidder_shares_owed = bid_shares[bid_id]['shares']
			# print()
			# print(f'Bidder {bid_id} is owed {bidder_shares_owed} shares')

			if bidder_shares_owed == 0:
				continue

			# Get the trader from the dictionary of all traders
			bidder = self.get_bidder(bid_id)
			if bidder == -1:
				print('lalalal didnt find bidder')
				continue
			

			for ask_id in askers:
				ask_shares_owed = ask_shares[ask_id]['shares']
				# print(f'Asker {ask_id} is owed {ask_shares_owed}')

				if ask_shares_owed == 0:
					# askers.remove(ask_id)
					continue
				elif ask_shares_owed >= bidder_shares_owed:
					# print(f'Buying {bidder_shares_owed} from asker {ask_id}')
					# Get the asker to update their funds
					asker = self.get_asker(ask_id)
					if not asker:
						continue
					bidder.balance += bidder_shares_owed
					bidder.funds -= bidder_shares_owed * p
					asker.balance += bidder_shares_owed * p
					asker.funds -= bidder_shares_owed

					ask_shares[ask_id]['shares'] -= bidder_shares_owed
					bidder_shares_owed = 0
					bid_shares[bid_id]['shares'] = 0
					# Update the funds in the orderbook
					self.book.bids[bid_id]['funds'] = bidder.funds
					self.book.asks[ask_id]['funds'] = asker.funds  

					# Cancel traders if they run out of funds
					if bidder.funds <= 0:
						self.cancel_trader(bidder)
					if asker.funds <= 0:
						self.cancel_trader(asker)
					break
				elif ask_shares_owed < bidder_shares_owed:
					# print(f'Buying {ask_shares_owed} from asker {ask_id}')
					asker = self.get_asker(ask_id)
					if not asker:
						continue
					bidder.balance += ask_shares_owed
					bidder.funds -= ask_shares_owed * p
					asker.balance += ask_shares_owed * p 
					asker.funds -= ask_shares_owed
					ask_shares[ask_id]['shares'] = 0
					bidder_shares_owed -= ask_shares_owed
					bid_shares[bid_id]['shares'] -= ask_shares_owed

					# askers.remove(ask_id)
					self.book.bids[bid_id]['funds'] = bidder.funds
					self.book.asks[ask_id]['funds'] = asker.funds  

					if bidder.funds <= 0:
						self.cancel_trader(bidder)
					if asker.funds <= 0:
						self.cancel_trader(asker)

		sum_excess = 0
		# print('\nBids\n')
		for bid_id in list(bid_shares):
			shares = bid_shares[bid_id]['shares']
			if shares != 0:
				print(f'Exchange is covering {shares} to bidder')
				self.book.bids[bid_id]['funds'] -= shares * p
				bidder = self.traders[bid_id]
				bidder.balance += shares

			# print(f'{bid_id} is owed {shares}')

		# print('\nAsks\n')
		for ask_id in list(ask_shares):
			shares = ask_shares[ask_id]['shares']
			if shares != 0:
				print(f'Exchange is covering {shares} to asker')
				self.book.asks[ask_id]['funds'] -= shares
				asker = self.traders[ask_id]
				asker.balance += shares * p

			# print(f'{ask_id} is owed {shares}')

	def get_asker(self, asker_id):
		try:
			asker = self.traders[asker_id]
			return asker
		except KeyError:
			print('Error can not find asker to exchange with')
			return -1

	def get_bidder(self, bidder_id):
		try:
			bidder = self.traders[bidder_id]
			return bidder
		except KeyError:
			print('Error can not find bidder to exchange with')
			return -1
			
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
			self.send_rand_cancels(beta=.001)

			# Updates for current traders
			self.send_rand_updates(beta=.005)

			# Send in new traders
			if self.first_time:
				# self.first_time = False
				self.send_rand_traders(beta=.01)

			# Sleep after sending til batch is over
			time.sleep(self.exchange._batch_time)

	def send_rand_traders(self, beta=.01):
		num_traders = rd.num_arrivals(self.exchange._batch_time, beta)
		# num_traders = math.ceil(np.random.uniform(20, 50))
		print(f'Sending {num_traders} new orders!')
		traders = []
		traders = self.setup_rand_traders(num_traders)
		self.submit_traders_orders(traders)

	def setup_rand_traders(self, n):
		traders = []
		for x in range(0, n):
			traders.append(self.setup_rand_trader())

		return traders

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

	def send_rand_cancels(self, beta=.001):
		# Cancel from current traders
		try:
			num_traders = rd.num_arrivals(self.exchange._batch_time, beta)
			# print(f'Cancelling {num_traders} orders!')
			for x in range(0, num_traders):
				trader_id = np.random.choice(list(self.traders))
				self.cancel_trader(self.traders[trader_id])
		except ValueError:
			print('Tried to cancel but not enough traders in book')

	def cancel_trader(self, trader):
		try:
			trader.cancel_order()
			# print(f'CANCEL @{str(datetime.datetime.now())}: {trader.current_order}')
			self.exchange.get_order(trader.current_order)
			self.traders.pop(trader.account)
		except KeyError:
			print(f'Tried to cancel but could not find {trader}')

	def send_rand_updates(self, beta=.005):
		# Updates for current traders
		try:
			num_traders = rd.num_arrivals(self.exchange._batch_time, beta)
			# print(f'Updating {num_traders} orders!')
			for x in range(0, num_traders):
				trader_id = np.random.choice(list(self.traders))
				self.update_trader(self.traders[trader_id])
		except ValueError:
			print('Tried to update but failed')

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