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
				try:
					demand_vector.append(((p_high - price_tick) / (p_high - p_low)) * u_max)
				except ZeroDivisionError:
					print(f'div by zero ERROR: p_high={p_high}, p_low={p_low}')
					exit()
			else:
				demand_vector.append(0)

		# Add array of zeros to current aggregate_demand
		try:
			if self.aggregate_demand is None:
				print('Creating initial agg_demand ndarray')
				self.aggregate_demand = np.zeros([math.ceil((self.max_price + 1) / Exchange._min_tick_size), self.num_active_bids])
			
			# Increase aggregate demand schedule columns by 1
			self.aggregate_demand = np.c_[self.aggregate_demand, demand_vector]
			# Save the index of the order for future cancellation
			self.active_bids.append(order['order_id'])
		except Exception as e:
			print('Failed to append demand schedule: ')#, demand_vector)

			
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
				print('Creating initial agg_supply ndarray')
				self.aggregate_supply = np.zeros([math.ceil((self.max_price + 1) / Exchange._min_tick_size), self.num_active_asks])
			
			# Increase aggregate supply schedule columns by 1
			self.aggregate_supply = np.c_[self.aggregate_supply, supply_vector]
			# Save the index of the order for future cancellation
			self.active_asks.append(order['order_id'])
		except Exception as e:
			print('Failed to append supply schedule: ')#, supply_vector)

	def remove_from_agg_demand(self, index):
		temp_list = self.aggregate_demand.tolist()
		for row in temp_list:
			del row[index]
		self.aggregate_demand = np.array(temp_list)

	def remove_from_agg_supply(self, index):
		temp_list = self.aggregate_supply.tolist()
		for row in temp_list:
			del row[index]
		self.aggregate_supply = np.array(temp_list)

	def resize_schedules(self):
		'''Resizes each schedule '''
		self.resize_demand()
		self.resize_supply()

	def resize_demand(self):
		'''This will resize a demand schedule to fit the max_price parameter.
		The schedule's u_max will be prepended to the schdule and 0's will be appended
		to the schedule until the length is correct. '''
		
		# Create an empty matrix that is the size of the new max_price
		# new_matrix = np.zeros([math.ceil((self.max_price + 1) / Exchange._min_tick_size), self.num_active_bids])
		num_rows = math.ceil((self.max_price + 1) / Exchange._min_tick_size)


		# Resize the aggregate demand to these new dimensions
		try:
			self.aggregate_demand.resize([num_rows, self.num_active_bids], refcheck=False)
		except AttributeError:
			print('No need to resize since aggregate matrix is empty!')
		except ValueError as e:
			print('AHHHH VALUE ERROR!!', e)
			pass


	def resize_supply(self):
		'''This will resize a supply schedule to fit the p_low and p_high parameters.
		0's will be prepended to the schdule and the schedule's u_max will be appended
		to the schedule until the length is correct. '''
		try:
			# Create an empty matrix that is the size of the new max_price
			supply_length =  len(self.aggregate_supply[:,0])
			new_size = math.ceil((self.max_price + 1) / Exchange._min_tick_size)

			# Append to the aggregate_supply matrix to match new larger max_price
			if supply_length < new_size:
				length_to_add =  new_size - supply_length

				row_to_append = np.transpose(self.aggregate_supply[-1, :])

				# Create length_to_add number duplicates of last row to append
				rows = np.tile(row_to_append, [length_to_add, 1])

				# Append the rows and resize the matrix for new shape
				self.aggregate_supply = np.append(self.aggregate_supply, rows)
				self.aggregate_supply.resize([new_size, self.num_active_asks])

			# Shrink the aggregate_supply matrix to the new lower max_price
			else:
				self.aggregate_supply.resize([new_size, self.num_active_asks], refcheck=False)

		except AttributeError:
			print('No need to resize since aggregate matrix is empty!')
			return
		except TypeError:
			print('No need to resize since aggregate matrix is empty!')
			return
		
	def calc_aggregate_demand(self):
		# Sums every schedule's demand at each price increment
		try:
			cum_demand = self.aggregate_demand.sum(axis=1)
			return cum_demand
		except AttributeError:
			return None

	def calc_aggregate_supply(self):
		# Sums every schedule's supply at each price increment
		try:
			cum_supply = self.aggregate_supply.sum(axis=1)
			return cum_supply
		except AttributeError:
			return None

	def calc_aggregates(self):
		length = math.ceil((self.max_price + 1) / Exchange._min_tick_size)
		# agg_demand = np.arange(0, length, Exchange._min_tick_size)
		# agg_supply = np.arange(0, length, Exchange._min_tick_size)
		agg_demand = [0] * length
		agg_supply = [0] * length
		for x in range(0, length):
			p_i = x * Exchange._min_tick_size
			for t in self.book.book:
				# Demand schedules add their u_max if p_i < p_low
				if p_i < t['p_low'] and t['order_type'] == 'buy':
					agg_demand[x] += t['u_max']

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
		self.total_aggregate_demand = self.calc_aggregate_demand()
		self.total_aggregate_supply = self.calc_aggregate_supply()

		# self.total_aggregate_supply, self.total_aggregate_demand = self.calc_aggregates()

		self.best_bid = 0
		self.best_ask = 0

		try:
			# returns an array containing only elements where demand <= supply
			cross_indices = np.where(self.total_aggregate_demand[:-1] <= self.total_aggregate_supply[1:])
			# Crossing point will be the first occurence of this
			self.clearing_price = cross_indices[0][0] * Exchange._min_tick_size
			self.clearing_rate = (self.total_aggregate_supply[cross_indices[0][0]] 
								+ self.total_aggregate_demand[cross_indices[0][0]]) / 2
			self.best_bid = self.total_aggregate_demand[cross_indices[0][0]]
			self.best_ask = self.total_aggregate_supply[cross_indices[0][0]]

			print(f'p*:{self.clearing_price}, u*:{self.clearing_rate}')
			print(f'best bid: {self.best_bid}, best ask:{self.best_ask}')

			return self.best_bid, self.best_ask
		except IndexError:
			print('Can not compute crossing point')
			return False


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
					self.remove_schedule(message)
					self.book.new_messages.remove(message)
					# Check if the cancelled order had the max_price
					self.check_cancel_max_price(message) 
				elif order_type == 'buy':
					self.check_price(message)
					self.calc_demand(message)
					self.num_active_bids += 1
					self.book.new_messages.remove(message)
				elif order_type == 'sell': 
					self.check_price(message)
					self.calc_supply(message)
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
	@prof
	def remove_schedule(self, message):
		order_id = message['order_id']
		if message['old_type'] == 'buy':
			index = self.active_bids.index(order_id)
			print(f'Deleting {order_id} from index {index} in self.bids')
			self.active_bids.pop(index)
			self.num_active_bids -= 1
			self.remove_from_agg_demand(index)
		elif message['old_type'] == 'sell':
			index = self.active_asks.index(order_id)
			print(f'Deleting {order_id} from index {index} in self.asks')
			self.active_asks.pop(index)
			self.num_active_asks -= 1
			self.remove_from_agg_supply(index)
		else:
			print(f'Could not find {order_id} in bids or asks')

	def check_price(self, message):
		'''Checks incoming messages for p_high to see if
		the rest of the schedules should be updated to match
		the length of this new max_price '''
		if message['p_low'] < self.min_price:
			# print('Old p_low: ', self.min_price, 'new p_low: ', message['p_low'])
			self.min_price = message['p_low']

		if message['p_high'] > self.max_price:
			print('Old p_high: ', self.max_price, 'new p_high: ', message['p_high'])
			self.max_price = message['p_high'] 
			print('Uh Oh, need to resize my aggregates!')
			self.resize_schedules()		

	def find_new_max_price(self):
		# Finds the max p_high in the order book
		new_max = 0
		for order in self.book.book:
			if order['p_high'] > new_max:
				new_max = order['p_high']
		return new_max

	def check_cancel_max_price(self, message):
		'''Finds a new max_price and resizes if a 
		cancel message causes the max_price to be lowered'''
		if message['p_high'] == self.max_price:
			print(f'Cancelling schedule with max_price: {self.max_price}')
			self.max_price = self.find_new_max_price()
			if self.max_price == message['p_high']:
				print('Dont worry, there was another order priced the same')
				return
			print(f'Resizing to new max_price: {self.max_price}')
			self.resize_schedules()	
		else:
			return

	def _get_balance(self):
		return self.balance











