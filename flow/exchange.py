import sys
from order_book import OrderBook
from util.exceptions import InvalidMessageType, NoCrossFound
from util.profiler import prof
from payer import Payer

import numpy as np
import itertools
import math
from copy import deepcopy
import datetime

import pickle



class Exchange(OrderBook):
	"""
		A market for trading with continuous scaled limit orders.

	Attributes:

	"""

	_batch_time = 1
	_min_tick_size = .01

	def __init__(self, name, address, balance=0.0):
		self.book = object
		self.name = name
		self.address = address
		self.balance = balance
		self.clearing_price = 0
		self.clearing_rate = 0
		self.batch_num = 0
		self.bids = {}
		self.asks = {}
		self.min_price = 0
		self.max_price = 0
		self.best_bid = 0
		self.best_ask = 0

	def add_book(self, book):
		self.book = book

	def get_order(self, order):
		self.book.receive_message(order)

	def calc_aggs(self, bids, asks, p_i):
		return self.calc_agg_demand(bids, p_i), self.calc_agg_supply(asks, p_i)

	def calc_agg_demand(self, bids, p_i):
		agg_demand = 0
		for o_id, bid in bids.items():
			# Constrain trader's u_max to be within their funds budget
			if bid['funds'] < bid['u_max'] * bid['p_low']:
				# print('Updating Bid u_max from ', bid['u_max'], '-> ', bid['funds'] / bid['p_low'], o_id)
				bid['u_max'] = bid['funds'] / bid['p_low']

			agg_demand += Payer.calc_demand(bid['p_low'], bid['p_high'], bid['u_max'], p_i)

		return agg_demand

	def calc_agg_supply(self, asks, p_i):
		agg_supply = 0
		for o_id, ask in asks.items():
			# Constrain trader's u_max to be within their funds budget
			if ask['funds'] < ask['u_max']:
				# print('Updating Ask u_max from ', ask['u_max'], '->', ask['funds'], o_id, ask['p_high'])
				ask['u_max'] = float(ask['funds'])

			agg_supply += Payer.calc_supply(ask['p_low'], ask['p_high'], ask['u_max'], p_i)

		return agg_supply

	def calc_crossing(self, min_p, max_p, tick_size, bids, asks, debug=True):
		clearing_rate, best_bid, best_ask = 0, 0, 0
		clearing_price = self.binary_search_cross(min_p, max_p, 
												  tick_size, bids, 
												  asks, debug)
		if clearing_price > 0:
			best_bid, best_ask = self.calc_aggs(bids, asks, clearing_price)
			clearing_rate = (best_bid + best_ask) / 2

		return clearing_price, clearing_rate, best_bid, best_ask

	def binary_search_cross(self, min_p, max_p, tick_size, bids, asks, debug=True):
		L = min_p
		R = max_p
		iterations = 0
		max_iterations = math.ceil(math.log2((R - L) / tick_size))
		while L < R:
			# Finds a midpoint with the correct price tick precision
			index = math.floor(((L + R) / 2) / tick_size) * tick_size
			# print(index)
			dem, sup = self.calc_aggs(bids, asks, index)
			if dem > sup:
				# We are left of the crossing
				L = index + tick_size 
			elif dem < sup:
				# We are right of the crossing
				R = index
			else:
				print(f'Found cross at {L}!')
				return self.nice_precision(L)

			if iterations > max_iterations:
				print(f'Uh oh did not find crossing within max_iterations! {self.nice_precision(L)}, ({L})')
				if debug:
					self.debug_cross(min_p, max_p, tick_size, bids, asks)
				return self.nice_precision(L)
				# return 0`

			iterations += 1

		# If there isn't an exact crossing, return leftmost index after cross
		print(f'Found crossing after {iterations} iterations')
		return self.nice_precision(L) 

	# @prof
	def hold_batch(self):
		# Create deep copy (snapshot) of book's bids and asks at this time
		self.bids, self.asks = self.snapshot_books(self.book)

		# Record the min and max prices from the books
		self.min_price = self.book.min_price
		self.max_price = self.book.max_price

		# Save the state of the books before
		# self.print_books()

		# Find the average aggregate schedules and then find p*
		
		results = self.calc_crossing(self.min_price, self.max_price, 
							Exchange._min_tick_size, 
							self.bids, self.asks)

		self.clearing_price, self.clearing_rate, self.best_bid, self.best_ask = results
		
		# Save the results of the batch
		self.print_results()

		# Calculate each trader's owed shares based on clearing price
		b_shares, a_shares, sum_bids, sum_asks = Payer.find_shares_owed(self.bids, self.asks, self.clearing_price)

		# print('bids\n', b_shares, '\nasks\n', a_shares, sum_bids, sum_asks)

		print(f'agg_demand: {self.best_bid}, paid_bids: {sum_bids}, agg_supply: {self.best_ask}, paid_asks: {sum_asks}, difference: {self.best_bid + self.best_ask - sum_bids - sum_asks}')

		self.batch_num += 1

		return b_shares, a_shares

	def snapshot_books(self, order_book):
		# By making a list of the keys, it saves the keys at the current moment
		# and if the dict changes size during the batch we'll be fine
		bids = {}
		asks = {}
		for key in list(order_book.bids):
			try:
				bids[key] = deepcopy(order_book.bids[key])

			except KeyError:
				print(f'Tried to copy {key} but could not find it!')

		for key in list(order_book.asks):
			try:
				asks[key] = deepcopy(order_book.asks[key])
			except KeyError:
				print(f'Tried to copy {key} but could not find it!')

		return bids, asks

	def nice_precision(self, num):
		return round(num / Exchange._min_tick_size) * Exchange._min_tick_size

	def print_books(self):
		print(f'Book for batch {self.batch_num} @{str(datetime.datetime.now())}:')
		print()
		print(f'Order Book({self.book.base_currency} -> {self.book.desired_currency})')
		print(f'Number of bids: {len(self.bids)}, Number of Asks: {len(self.asks)}')
		print('BIDS')

		for order_id in self.bids:
			print(f'{order_id}: {self.bids[order_id]}')

		print()
		print('ASKS')
		for order_id in self.asks:
			print(f'{order_id}: {self.asks[order_id]}')
		print()

		self.write_to_file('bids', self.bids)
		self.write_to_file('asks', self.asks)

	def print_results(self):
		time = str(datetime.datetime.now())
		print(f'Results of batch {self.batch_num} @{time}:')
		print(f'p*:{self.clearing_price}, u*:{self.clearing_rate}')
		print(f'best bid: {self.best_bid}, best ask:{self.best_ask}')
		print()
		print()
		result = {'timestamp': time, 'batch_num': self.batch_num, 
					'p*': self.clearing_price, 'u*': self.clearing_rate,
					'best_ask': self.best_ask, 'best_bid': self.best_bid,
					'min_price': self.min_price, 'max_price': self.max_price}
		self.write_to_file('result', result)

	def write_to_file(self, dest, data):
		file_name = f'../flow/data/{dest}_{self.batch_num}'
		file = open(file_name, 'wb')
		pickle.dump(data, file)
		file.close()

	def debug_cross(self, min_p, max_p, tick_size, bids, asks):
		print('Writing to file')
		data = {'min_p': min_p, 'max_p': max_p, 
				'tick_size': tick_size, 'bids': bids,
				'asks': asks}
		self.write_to_file('cross_fail', data)

	def _get_balance(self):
		return self.balance











