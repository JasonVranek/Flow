from order_book import OrderBook

import numpy as np
import itertools
import math

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
		self.supply = []
		self.demand = []
		self.aggregate_demand = []
		self.aggregate_supply = []
		self.clearing_price = 0
		self.clearing_rate = 0
		self.avg_aggregate_demand = 0
		self.avg_aggregate_supply = 0
		self.message_queue = []

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
		price_vector = []

		# p_low<= p* <= p_high
		for x in range(0, math.ceil((p_high - p_low) / Exchange._min_tick_size)):
			# price is every min tick increment between p_low and p_high
			price = p_low + x * Exchange._min_tick_size
			price_vector.append(price)
			demand_vector.append(((p_high - price) / (p_high - p_low)) * u_max)

		demand_schedule = np.column_stack((demand_vector, price_vector))

		self.aggregate_demand.append([order['order_id'], demand_schedule])

		return demand_schedule

	def calc_supply(self, order):
		'''Calculates the supply schedule for an entry in the order book.
		An nx2 array is returned that contains the order's rate at each minimum
		price increment.  This is appended to the list of all supply schedules
		and is indexed by the order's order_id'''
		p_low = order['p_low']; p_high = order['p_high']; u_max = order['u_max']
		supply_vector = []
		price_vector = []

		# p_low<= p* <= p_high
		for x in range(0, math.ceil((p_high - p_low) / Exchange._min_tick_size)):
			# price is every min tick increment between p_low and p_high
			price = p_low + x * Exchange._min_tick_size
			price_vector.append(price)
			supply_vector.append(u_max + ((price - p_high) / (p_high - p_low)) * u_max)

		supply_schedule = np.column_stack((supply_vector, price_vector))

		self.aggregate_supply.append([order['order_id'], supply_schedule])

		return supply_schedule

	def calc_each_demand(self):
		for order in self.book.bids:
			self.calc_demand(order)

	def calc_each_supply(self):
		for order in self.book.asks:
			self.calc_supply(order)

	def find_longest_schedule(self, is_demand=True):
		u_max = 0
		length = 0	
		if is_demand:
			for schedule in self.aggregate_demand:
				if schedule[1][0,0] > u_max:
					u_max = schedule[1][0,0]
				if len(schedule[1][:,0]) > length:
					length = len(schedule[1][:,0])
		else:
			for schedule in self.aggregate_supply:
				# The u_max is the last item in the array
				if schedule[1][-1,0] > u_max:
					u_max = schedule[1][-1,0]
				if len(schedule[1][:,0]) > length:
					length = len(schedule[1][:,0])

		# search
		return length, u_max

	def get_price_range(self):
		'''Increments through every schedule to find the lowest p_low
		and highest p_high. These are used to resize each schedule to these
		extremes for graphing and calculating the crossing point.'''
		p_low = 10000000; p_high = 0
		for schedule in self.aggregate_demand:
			if len(schedule[1]) == 0:
				print('Removing empty schedule: ', schedule)
				self.aggregate_demand.remove(schedule)
				# Send message to queue to be recalculated
				self.message_queue.append(schedule)
				continue
			if schedule[1][0,1] < p_low:
				p_low = schedule[1][0,1]
			if schedule[1][-1,1] > p_high:
				p_high = schedule[1][-1,1]

		for schedule in self.aggregate_supply:
			if len(schedule[1]) == 0:
				print('Removing empty schedule: ', schedule)
				self.aggregate_supply.remove(schedule)
				# Send message to queue to be recalculated
				self.message_queue.append(schedule)
				continue
			if schedule[1][0,1] < p_low:
				p_low = schedule[1][0,1]
			if schedule[1][-1,1] > p_high:
				p_high = schedule[1][-1,1]
		return p_low, p_high

	def resize_schedules(self, p_low, p_high, is_demand=True):
		'''Resizes each schedule '''
		if is_demand:
			for schedule in self.aggregate_demand:
				sched_u_max = schedule[1][0,0]
				cur_p_low = schedule[1][0,1]
				cur_p_high = schedule[1][-1,1]
				schedule[1] = self.resize_demand(schedule, cur_p_low, 
												cur_p_high, sched_u_max, 
												p_low, p_high)
		else:
			for schedule in self.aggregate_supply:
				sched_u_max = schedule[1][-1,0]
				cur_p_low = schedule[1][0,1]
				cur_p_high = schedule[1][-1,1]
				schedule[1] = self.resize_supply(schedule, cur_p_low, 
												cur_p_high, sched_u_max, 
												p_low, p_high)

	def resize_demand(self, schedule, cur_p_low, cur_p_high, sched_u_max, p_low, p_high):
		'''This will resize a demand schedule to fit the p_low and p_high parameters.
		The schedule's u_max will be prepended to the schdule and 0's will be appended
		to the schedule until the length is correct. '''
		array_length = math.ceil((p_high - p_low) / Exchange._min_tick_size)
		num_to_prepend = (cur_p_low - p_low) / Exchange._min_tick_size
		num_to_append = (p_high - cur_p_high) / Exchange._min_tick_size
		prepend_array = []
		append_array = []

		for x in range(0, math.floor(num_to_prepend)):
			prepend_array.append(sched_u_max)

		for x in range(0, math.floor(num_to_append)):
			append_array.append(0)

		new_schedule = list(itertools.chain(prepend_array, schedule[1][:,0], append_array))
		
		# Make sure the lengths are the correct length
		if(len(new_schedule) > array_length):
			price_array = np.arange(p_low, p_high + Exchange._min_tick_size, Exchange._min_tick_size)
		else:
			price_array = np.arange(p_low, p_high, Exchange._min_tick_size)
		
		combined_schedule = np.column_stack((new_schedule, price_array))

		return combined_schedule

	def resize_supply(self, schedule, cur_p_low, cur_p_high, sched_u_max, p_low, p_high):
		'''This will resize a supply schedule to fit the p_low and p_high parameters.
		0's will be prepended to the schdule and the schedule's u_max will be appended
		to the schedule until the length is correct. '''
		array_length = math.ceil((p_high - p_low) / Exchange._min_tick_size)
		num_to_prepend = (cur_p_low - p_low) / Exchange._min_tick_size
		num_to_append = (p_high - cur_p_high) / Exchange._min_tick_size
		prepend_array = []
		append_array = []

		for x in range(0, math.floor(num_to_prepend)):
			prepend_array.append(0)

		for x in range(0, math.floor(num_to_append)):
			append_array.append(sched_u_max)

		new_schedule = list(itertools.chain(prepend_array, schedule[1][:,0], append_array))
		
		# Make sure the lengths are the correct length
		if(len(new_schedule) > array_length):
			price_array = np.arange(p_low, p_high + Exchange._min_tick_size, Exchange._min_tick_size)
		else:
			price_array = np.arange(p_low, p_high, Exchange._min_tick_size)
		
		combined_schedule = np.column_stack((new_schedule, price_array))

		return combined_schedule

	def calc_aggregate_demand(self):
		# Averages every schedule's rate at each price increment
		price_array = self.aggregate_demand[0][1][:,1]
		average_demand = np.empty(shape=(len(price_array)))
		for schedule in self.aggregate_demand:
			average_demand = np.add(average_demand, schedule[1][:,0])
		average_demand = np.divide(average_demand, len(self.aggregate_demand))
		
		return np.column_stack((average_demand, price_array))

	def calc_aggregate_supply(self):
		# Averages every schedule's rate at each price increment
		price_array = self.aggregate_supply[0][1][:,1]
		average_supply = np.empty(shape=(len(price_array)))
		for schedule in self.aggregate_supply:
			average_supply = np.add(average_supply, schedule[1][:,0])
		average_supply = np.divide(average_supply, len(self.aggregate_supply))
		
		return np.column_stack((average_supply, price_array))

	def calc_crossing(self):
		# Get average schedules
		self.avg_aggregate_demand = self.calc_aggregate_demand()
		self.avg_aggregate_supply = self.calc_aggregate_supply()
		best_bid = 0
		best_ask = 0

		# Find the first index where demand <= supply
		for x in range(0, len(self.avg_aggregate_demand[:,0])):
			if self.avg_aggregate_demand[x,0] <= self.avg_aggregate_supply[x,0]:
				# Set the clearing price to be the average of these two indices
				self.clearing_price = (self.avg_aggregate_supply[x,1] + self.avg_aggregate_demand[x,1]) / 2
				self.clearing_rate = (self.avg_aggregate_supply[x,0] + self.avg_aggregate_demand[x,0]) / 2
				best_bid = self.avg_aggregate_demand[x,0]
				best_ask = self.avg_aggregate_supply[x,0]
				break
		print(f'p*:{self.clearing_price}, u*:{self.clearing_rate}')
		print(f'best bid: {best_bid}, best ask:{best_ask}')

		return best_bid, best_ask


	def hold_batch(self):
		# Aggregate the supply and demand for what is in the book
		# self.calc_each_supply()
		# self.calc_each_demand()
		while len(self.book.new_messages) > 0:
			self.process_messages()

		# Find the min and max prices		
		p_low, p_high = self.get_price_range()

		# Resize all schedules to be same length for easier math
		self.resize_schedules(p_low, p_high, True)
		self.resize_schedules(p_low, p_high, False)
		
		# Find the average aggregate schedules and then find p*
		self.calc_crossing()

	def get_new_messages(self):
		pass

	def process_messages(self):
		'''FIFO Queue for the exchange to process NEW orders from exchange'''
		for message in self.book.new_messages:
			try:
				order_type = message['order_type']
				if order_type == 'C':
					self.remove_schedule(message)
					# Await response then delete from new_messages queue
					self.book.new_messages.remove(message)
				elif order_type == 'buy':
					self.calc_demand(message)
					self.book.new_messages.remove(message)
				elif order_type == 'sell': 
					self.calc_supply(message)
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
		pass

	def _get_balance(self):
		return self.balance
