from order_book import OrderBook
from exceptions import InvalidMessageType

import numpy as np
import itertools
import math

from profiler import prof

class Exchange(OrderBook):
	"""
		A market for trading with continuous scaled limit orders.

	Attributes:

	"""

	_batch_time = 5
	_min_tick_size = .01

	def __init__(self, name, address, balance=0.0):
		self.book = object
		self.name = name
		self.address = address
		self.balance = balance
		self.aggregate_demand = None
		self.aggregate_supply = None
		self.clearing_price = 0
		self.clearing_rate = 0
		self.total_aggregate_demand = []
		self.total_aggregate_supply = []
		self.message_queue = []
		self.max_price = 0
		self.min_price = 10000000
		self.num_active_bids = 0
		self.num_active_asks = 0
		self.active_bids = []
		self.active_asks = []

	def add_book(self, book):
		self.book = book

	def get_order(self, order):
		self.book.receive_message(order)

	# @prof
	def calc_aggregates(self):
		length = math.ceil((self.max_price + 1) / Exchange._min_tick_size)
		agg_demand = [0] * length
		agg_supply = [0] * length

		for x in range(0, length):
			p_i = x * Exchange._min_tick_size
			for t in self.book.book:
				# Demand schedules add their u_max if p_i < p_low
				if p_i < t['p_low'] and t['order_type'] == 'buy':
					agg_demand[x] += t['u_max']

				# Aggregate based on price index
				if p_i >= t['p_low'] and p_i <= t['p_high']: 
					if t['order_type'] == 'C':
						print('cancel!')
					if t['order_type'] == 'buy':
						agg_demand[x] += t['u_max'] * ((t['p_high'] - p_i) / (t['p_high'] - t['p_low']))
					if t['order_type'] == 'sell':
						agg_supply[x] += t['u_max'] + ((p_i - t['p_high']) / (t['p_high'] - t['p_low'])) * t['u_max']

				# Supply schedules add their u_max if p_i > p_high
				if p_i > t['p_high'] and t['order_type'] == 'sell':
					agg_supply[x] += t['u_max']

		return agg_demand, agg_supply

	def calc_crossing(self):
		# Get aggregate schedules
		self.total_aggregate_demand, self.total_aggregate_supply = self.calc_aggregates()

		self.best_bid = 0
		self.best_ask = 0

		try:
			index = self.binary_search_cross(self.total_aggregate_demand, 
												self.total_aggregate_supply, 
												len(self.total_aggregate_demand))
			# # returns an array containing only elements where demand <= supply
			self.clearing_price = index * Exchange._min_tick_size
			self.clearing_rate = (self.total_aggregate_supply[index] 
								+ self.total_aggregate_demand[index]) / 2
			self.best_bid = self.total_aggregate_demand[index]
			self.best_ask = self.total_aggregate_supply[index]

			print(f'p*:{self.clearing_price}, u*:{self.clearing_rate}')
			print(f'best bid: {self.best_bid}, best ask:{self.best_ask}')

			# return self.best_bid, self.best_ask
		except IndexError:
			print('Can not compute crossing point')
			return False

	def binary_search_cross(self, dem, sup, n):
		L = 0
		R = n
		while L < R:
			index = math.floor((L + R) / 2)
			if dem[index] > sup[index]:
				# We are left of the crossing
				L = index + 1 
			elif dem[index] < sup[index]:
				# We are right of the crossing
				R = index
			else:
				print(f'Founds it at {L}!')
				return L
		# If there isn't an exact crossing, return leftmost index after cross
		return L 


	# @prof
	def hold_batch(self):
		# Aggregate the supply and demand for what is the book's new_message queue
		while len(self.book.new_messages) > 0:
			self.process_messages()
		
		# Find the average aggregate schedules and then find p*
		self.calc_crossing()

	def process_messages(self):
		'''FIFO Queue for the exchange to process NEW orders from exchange'''
		for message in self.book.new_messages:
			# print('processing:', message)
			try:
				order_type = message['order_type']
				if order_type == 'C':
					self.book.new_messages.remove(message)
					# Check if the cancelled order had the max_price
					self.check_cancel_max_price(message) 
				elif order_type == 'buy':
					self.check_price(message)
					self.num_active_bids += 1
					self.book.new_messages.remove(message)
				elif order_type == 'sell': 
					self.check_price(message)
					self.num_active_asks += 1
					# Await response then delete from message_queue
					self.book.new_messages.remove(message)
				else:
					# Remove invalid messages from the queue
					self.book.new_messages.remove(message)
					raise InvalidMessageType

			except InvalidMessageType:
				print('Error, exchange trying to process invalid message:', message)
				pass

	def check_price(self, message):
		'''Checks incoming messages for p_high to see if
		the length of our total aggregate will change '''
		if message['p_low'] < self.min_price:
			self.min_price = message['p_low']

		if message['p_high'] > self.max_price:
			# print('Old p_high: ', self.max_price, 'new p_high: ', message['p_high'])
			self.max_price = message['p_high'] 

	def find_new_max_price(self):
		# Finds the max p_high in the order book
		new_max = 0
		for order in self.book.book:
			if order['p_high'] > new_max:
				new_max = order['p_high']
		return new_max

	def check_cancel_max_price(self, message):
		'''Finds a new max_price if a cancel message 
		causes the max_price to be lowered'''
		if message['p_high'] == self.max_price:
			# print(f'Cancelling schedule with max_price: {self.max_price}')
			self.max_price = self.find_new_max_price()
			if self.max_price == message['p_high']:
				print('Dont worry, there was another order priced the same')
				return
		else:
			return

	def _get_balance(self):
		return self.balance











