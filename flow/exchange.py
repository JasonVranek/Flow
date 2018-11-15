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
		self.total_aggregate_demand = []
		self.total_aggregate_supply = []
		self.batch_num = 0
		self.bids = {}
		self.asks = {}
		self.min_price = 0
		self.max_price = 0
		self.best_bid = 0
		self.best_ask = 0
		self.bid_history = []
		self.ask_history = []

	def add_book(self, book):
		self.book = book

	def get_order(self, order):
		self.book.receive_message(order)

	def calc_aggs(self, p_i):
		return self.calc_agg_demand(p_i), self.calc_agg_supply(p_i)

	def calc_agg_demand(self, p_i):
		agg_demand = 0
		for o_id, bid in self.bids.items():
			# Constrain trader's u_max to be within their funds budget
			if bid['funds'] < bid['u_max'] * bid['p_low']:
				print('Updating Bid u_max from ', bid['u_max'], '-> ', bid['funds'] / bid['p_low'], o_id)
				bid['u_max'] = bid['funds'] / bid['p_low']
			# else:
			# 	print('Not Updating Bid ', bid['u_max'], bid['funds'], bid['p_low'], o_id)

			agg_demand += Payer.calc_demand(bid['p_low'], bid['p_high'], bid['u_max'], p_i)

		return agg_demand

	def calc_agg_supply(self, p_i):
		agg_supply = 0
		for o_id, ask in self.asks.items():
			# Constrain trader's u_max to be within their funds budget
			if ask['funds'] < ask['u_max']:
				print('Updating Ask u_max from ', ask['u_max'], '->', ask['funds'], o_id, ask['p_high'])
				ask['u_max'] = float(ask['funds'])

			agg_supply += Payer.calc_supply(ask['p_low'], ask['p_high'], ask['u_max'], p_i)

		return agg_supply

	def calc_crossing(self):
		self.clearing_price = 0
		self.clearing_rate = 0
		self.best_bid = 0
		self.best_ask = 0
		try:
			self.clearing_price = self.binary_search_cross()
			if self.clearing_price < 0:
				self.clearing_price = 0
				raise NoCrossFound
			self.best_bid, self.best_ask = self.calc_aggs(self.clearing_price)
			self.clearing_rate = (self.best_bid + self.best_ask) / 2
			

		except Exception as e:
			print('Error calculating crossing', e)

	def binary_search_cross(self):
		L = self.min_price 
		R = self.max_price 
		iterations = 0
		max_iterations = math.ceil(math.log2((R - L) / Exchange._min_tick_size))
		# max_iterations = 1000
		# print(f'max_iterations: {max_iterations}, p_low: {L}, p_high: {R}')
		while L < R:
			# Finds a midpoint with the correct price tick precision
			index = math.floor(((L + R) / 2) / Exchange._min_tick_size) * Exchange._min_tick_size
			# print(index)
			dem, sup = self.calc_aggs(index)
			if dem > sup:
				# We are left of the crossing
				L = index + Exchange._min_tick_size 
			elif dem < sup:
				# We are right of the crossing
				R = index
			else:
				print(f'Found cross at {L}!')
				return L
			iterations += 1
			if iterations > max_iterations:
				print(f'Uh oh did not find crossing within max_iterations! {L}')
				# return L
				return -1
		# If there isn't an exact crossing, return leftmost index after cross
		print(f'Found crossing after {iterations} iterations')
		return L 

	# @prof
	def hold_batch(self):
		# Create deep copy (snapshot) of book's bids and asks at this time
		# self.bids = deepcopy(self.book.bids)
		# self.asks = deepcopy(self.book.asks)
		self.snapshot_books()

		# Record the min and max prices from the books
		self.min_price = self.book.min_price
		self.max_price = self.book.max_price

		# Save the state of the books before
		# self.print_books()

		# Find the average aggregate schedules and then find p*
		self.calc_crossing()
		
		# Save the results of the batch
		self.print_results()

		# Calculate each trader's owed shares based on clearing price
		b_shares, a_shares, sum_bids, sum_asks = Payer.find_shares_owed(self.bids, self.asks, self.clearing_price)

		# print('bids\n', b_shares, '\nasks\n', a_shares, sum_bids, sum_asks)

		print(f'agg_demand: {self.best_bid}, paid_bids: {sum_bids}, agg_supply: {self.best_ask}, paid_asks: {sum_asks}, difference: {self.best_bid + self.best_ask - sum_bids - sum_asks}')

		self.batch_num += 1

		return b_shares, a_shares

	def snapshot_books(self):
		# By making a list of the keys, it saves the keys at the current moment
		# and if the dict changes size during the batch we'll be fine
		self.bids = {}
		self.asks = {}
		for key in list(self.book.bids):
			try:
				self.bids[key] = deepcopy(self.book.bids[key])

			except KeyError:
				print(f'Tried to copy {key} but could not find it!')

		for key in list(self.book.asks):
			try:
				self.asks[key] = deepcopy(self.book.asks[key])
			except KeyError:
				print(f'Tried to copy {key} but could not find it!')

	def nice_precision(self, num):
		return math.floor(num / Exchange._min_tick_size) * Exchange._min_tick_size

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

	def _get_balance(self):
		return self.balance











