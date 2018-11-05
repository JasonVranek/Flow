from order_book import OrderBook
from exceptions import InvalidMessageType

import numpy as np
import itertools
import math
from copy import deepcopy

from profiler import prof

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

	def add_book(self, book):
		self.book = book

	def get_order(self, order):
		self.book.receive_message(order)

	def calc_aggs(self, p_i):
		return self.calc_agg_demand(p_i), self.calc_agg_supply(p_i)

	def calc_agg_demand(self, p_i):
		agg_demand = 0
		for o_id, bid in self.bids.items():
			# Demand schedules add their u_max if p_i < p_low
			if p_i < bid['p_low']:
				agg_demand += bid['u_max']

			# The price index is within their [p_low, p_high]
			elif p_i >= bid['p_low'] and p_i <= bid['p_high']: 
				agg_demand += bid['u_max'] * ((bid['p_high'] - p_i) / (bid['p_high'] - bid['p_low']))

		return agg_demand

	def calc_agg_supply(self, p_i):
		agg_supply = 0
		for o_id, ask in self.asks.items():
			# The price index is within their [p_low, p_high]
			if p_i >= ask['p_low'] and p_i <= ask['p_high']:
				agg_supply += ask['u_max'] + ((p_i - ask['p_high']) / (ask['p_high'] - ask['p_low'])) * ask['u_max']

			# Supply schedules add their u_max if pi > p_high
			elif p_i > ask['p_high']:
				agg_supply += ask['u_max']

		return agg_supply

	def calc_crossing(self):
		try:
			self.clearing_price = self.binary_search_cross()
			self.best_bid, self.best_ask = self.calc_aggs(self.clearing_price)
			self.clearing_rate = (self.best_bid + self.best_ask) / 2

			print()
			print(f'Results of batch {self.batch_num}')
			print(f'p*:{self.clearing_price}, u*:{self.clearing_rate}')
			print(f'best bid: {self.best_bid}, best ask:{self.best_ask}')
			print()

		except Exception as e:
			print('Error calculating crossing', e)

	def binary_search_cross(self):
		L = self.min_price 
		R = self.max_price 
		iterations = 0
		max_iterations = math.ceil(math.log2((R - L) / Exchange._min_tick_size))
		print(f'max_iterations: {max_iterations}, p_low: {L}, p_high: {R}')
		while L < R:
			# Finds a midpoint with the correct price tick precision
			# index = self.nice_precision((L + R) / 2)
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
				print(f'Founds it at {L}!')
				return L
			iterations += 1
			if iterations > max_iterations:
				print('Uh oh did not find crossing within max_iterations!')
				return L
		# If there isn't an exact crossing, return leftmost index after cross
		print(f'Found crossing after {iterations} iterations')
		return L 

	# @prof
	def hold_batch(self):
		# Create deep copy (snapshot) of book's bids and asks at this time
		self.bids = deepcopy(self.book.bids)
		self.asks = deepcopy(self.book.asks)

		# Record the min and max prices from the books
		self.min_price = self.book.min_price
		self.max_price = self.book.max_price

		# Find the average aggregate schedules and then find p*
		self.calc_crossing()

		self.batch_num += 1

	def nice_precision(self, num):
		return math.floor(num / Exchange._min_tick_size) * Exchange._min_tick_size

	def _get_balance(self):
		return self.balance











