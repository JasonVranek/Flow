from order_book import OrderBook
from exceptions import InvalidMessageType

import numpy as np
import itertools
import math

class Exchange(OrderBook):
	"""
		A market for trading with continuous scaled limit orders.

	Attributes:

	"""

	_batch_time = 5
	_min_tick_size = .1

	def __init__(self, name, address, balance=0.0):
		self.book = object
		self.name = name
		self.address = address
		self.balance = balance
		self.aggregate_demand = None
		self.aggregate_supply = None
		self.clearing_price = 0
		self.clearing_rate = 0
		self.avg_aggregate_demand = []
		self.avg_aggregate_supply = []
		self.message_queue = []
		self.max_price = 0
		self.min_price = 10000000
		self.active_bids = 0
		self.active_asks = 0

	def add_book(self, book):
		self.book = book

	def get_order(self, order):
		self.book.receive_message(order)

	def calc_demand(self, order):
		'''Calculates the demand schedule for an entry in the order book.
		An nx2 array is returned that contains the order's rate at each minimum
		price increment.  This is appended to the list of all demand schedules 
		and is indexed by the order's order_id'''
		p_low = order['p_low']; p_high = order['p_high']; u_max = order['u_max']
		demand_vector = []

		# Create a new demand schedule column to be added to aggregate matrix
		for x in range(0, math.ceil((self.max_price + 1) / Exchange._min_tick_size)):
			price_tick = x * Exchange._min_tick_size
			if price_tick < p_low:
				demand_vector.append(u_max)
			elif price_tick >= p_low and price_tick <= p_high:
				demand_vector.append(((p_high - price_tick) / (p_high - p_low)) * u_max)
			else:
				demand_vector.append(0)

		# Add array of zeros to current aggregate_demand
		try:
			if self.aggregate_demand is None:
				print('Creating initial agg_demand ndarray')
				self.aggregate_demand = np.zeros([math.ceil((self.max_price + 1) / Exchange._min_tick_size), self.active_bids])
			
			# Increase aggregate demand schedule columns by 1
			self.aggregate_demand = np.c_[self.aggregate_demand, demand_vector]
		except Exception as e:
			print('Failed to append demand schedule: ', demand_vector)

			
	def calc_supply(self, order):
		'''Calculates the supply schedule for an entry in the order book.
		An nx2 array is returned that contains the order's rate at each minimum
		price increment.  This is appended to the list of all supply schedules
		and is indexed by the order's order_id'''
		p_low = order['p_low']; p_high = order['p_high']; u_max = order['u_max']
		supply_vector = []

		# Create a new demand schedule column to be added to aggregate matrix
		for x in range(0, math.ceil((self.max_price + 1) / Exchange._min_tick_size)):
			price_tick = x * Exchange._min_tick_size
			if price_tick < p_low:
				supply_vector.append(0)
			elif price_tick >= p_low and price_tick <= p_high:
				supply_vector.append(u_max + ((price_tick - p_high) / (p_high - p_low)) * u_max)
			else:
				supply_vector.append(u_max)

		# Add array of zeros to current aggregate_supply
		try:
			if self.aggregate_supply is None:
				print('Creating initial agg_demand ndarray')
				self.aggregate_supply = np.zeros([math.ceil((self.max_price + 1) / Exchange._min_tick_size), self.active_asks])
			
			# Increase aggregate supply schedule columns by 1
			self.aggregate_supply = np.c_[self.aggregate_supply, supply_vector]
		except Exception as e:
			print('Failed to append supply schedule: ', supply_vector)

	def resize_schedules(self):
		'''Resizes each schedule '''
		self.resize_demand()
		self.resize_supply()

	def resize_demand(self):
		'''This will resize a demand schedule to fit the max_price parameter.
		The schedule's u_max will be prepended to the schdule and 0's will be appended
		to the schedule until the length is correct. '''
		
		# Create an empty matrix that is the size of the new max_price
		new_matrix = np.zeros([math.ceil((self.max_price + 1) / Exchange._min_tick_size), self.active_bids])

		# Resize the aggregate demand to these new dimensions
		try:
			self.aggregate_demand.resize(new_matrix.shape)
		except AttributeError:
			print('No need to resize since aggregate matrix is empty!')


	def resize_supply(self):
		'''This will resize a supply schedule to fit the p_low and p_high parameters.
		0's will be prepended to the schdule and the schedule's u_max will be appended
		to the schedule until the length is correct. '''
		try:
			# Create an empty matrix that is the size of the new max_price
			new_matrix = np.zeros([math.ceil((self.max_price + 1) / Exchange._min_tick_size), self.active_asks])

			length_to_add = math.ceil((self.max_price + 1) / Exchange._min_tick_size) - len(self.aggregate_supply[:,0])
			print('Adding: ', length_to_add, 'rows')

			row_to_append = np.transpose(self.aggregate_supply[-1, :])
			print('appending:', row_to_append)

			for x in range(0, length_to_add):
				self.aggregate_supply = np.append(self.aggregate_supply, row_to_append)

			# Each schedule's u_max should be appended until the length is correct

			# Resize the aggregate supply to these new dimensions
			self.aggregate_supply.resize(new_matrix.shape)
		except AttributeError:
			print('No need to resize since aggregate matrix is empty!')
		except TypeError:
			print('No need to resize since aggregate matrix is empty!')
		
	def calc_aggregate_demand(self):
		# Averages every schedule's rate at each price increment
		# Create an empty array the size of the prices
		average_demand = np.zeros([len(self.aggregate_demand[:,0])])
		for schedule in self.aggregate_demand.T:
			average_demand = np.add(average_demand, schedule)

		# Divide by the number of schedules in the matrix
		average_demand = np.divide(average_demand, len(self.aggregate_demand[0,:]))

		return average_demand

	def calc_aggregate_supply(self):
		# Averages every schedule's rate at each price increment
		# Create an empty array the size of the prices
		average_supply = np.zeros([len(self.aggregate_supply[:,0])])
		for schedule in self.aggregate_supply.T:
			average_supply = np.add(average_supply, schedule)

		# Divide by the number of schedules in the matrix
		average_supply = np.divide(average_supply, len(self.aggregate_supply[0,:]))

		return average_supply

	def calc_crossing(self):
		# Get average schedules
		self.avg_aggregate_demand = self.calc_aggregate_demand()
		self.avg_aggregate_supply = self.calc_aggregate_supply()
		best_bid = 0
		best_ask = 0

		# Find the first index where demand <= supply
		for x in range(0, len(self.avg_aggregate_demand)):
			if self.avg_aggregate_demand[x] <= self.avg_aggregate_supply[x]:
				# Set the clearing price to be the average of these two indices
				self.clearing_price = x * Exchange._min_tick_size
				self.clearing_rate = (self.avg_aggregate_supply[x] + self.avg_aggregate_demand[x]) / 2
				best_bid = self.avg_aggregate_demand[x]
				best_ask = self.avg_aggregate_supply[x]
				break
		print(f'p*:{self.clearing_price}, u*:{self.clearing_rate}')
		print(f'best bid: {best_bid}, best ask:{best_ask}')

		return best_bid, best_ask


	def hold_batch(self):
		# Aggregate the supply and demand for what is the book's new_message queue
		while len(self.book.new_messages) > 0:
			self.process_messages()
		
		# Find the average aggregate schedules and then find p*
		self.calc_crossing()

	def process_messages(self):
		'''FIFO Queue for the exchange to process NEW orders from exchange'''
		for message in self.book.new_messages:
			print('processing:', message)
			try:
				order_type = message['order_type']
				if order_type == 'C':
					self.remove_schedule(message)
					# Await response then delete from new_messages queue
					self.book.new_messages.remove(message)
					# self.check_price(message) # need to update if it was the best bid
				elif order_type == 'buy':
					self.check_price(message)
					self.calc_demand(message)
					self.active_bids += 1
					self.book.new_messages.remove(message)
				elif order_type == 'sell': 
					self.check_price(message)
					self.calc_supply(message)
					self.active_asks += 1
					# Await response then delete from message_queue
					self.book.new_messages.remove(message)
				else:
					# Remove invalid messages from the queue
					self.book.new_messages.remove(message)
					raise InvalidMessageType

			except InvalidMessageType:
				print('Error, exchange trying to process invalid message:', message)
				pass

	def remove_schedule(self, message):
		# self.active_bids -= 1
		pass

	def check_price(self, message):
		if message['p_low'] < self.min_price:
			print('Old p_low: ', self.min_price, 'new p_low: ', message['p_low'])
			self.min_price = message['p_low']
			print('Uh Oh, need to resize my aggregates!')

		if message['p_high'] > self.max_price:
			print('Old p_high: ', self.max_price, 'new p_high: ', message['p_high'])
			self.max_price = message['p_high'] 
			print('Uh Oh, need to resize my aggregates!')
			self.resize_schedules()

		

	def _get_balance(self):
		return self.balance
