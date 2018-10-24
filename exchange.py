from order_book import OrderBook

import numpy as np

class Exchange(OrderBook):
	"""
		A market for trading with continuous scaled limit orders.

	Attributes:

	"""

	_batch_time = 5
	_min_tick_size = .01

	def __init__(self, name, address, balance=0.0):
		# OrderBook.__init__(self, base_currency, desired_currency)
		self.book = object
		self.name = name
		self.address = address
		self.balance = balance
		self.supply = []
		self.demand = []
		self.aggregate_demand = []
		self.aggregate_supply = []

	def add_book(self, book):
		self.book = book

	def get_order(self, order):
		self.book.receive_message(order)

	def calc_demand(self, order):
		p_low = order['p_low']; p_high = order['p_high']; u_max = order['u_max']
		demand_vector = []
		price_vector = []
		# (will buy at u_max while p* < p_low)
		# for x in range(0, int(p_low)):
		demand_vector.append(u_max)
		price_vector.append(p_low)

		# p_low<= p* <= p_high
		for x in range(0, int((p_high - p_low) / Exchange._min_tick_size)):
			# price is every min tick increment between p_low and p_high
			price = p_low + x * Exchange._min_tick_size
			price_vector.append(price)
			demand_vector.append(((p_high - price) / (p_high - p_low)) * u_max)

		# p* > p_high
		demand_vector.append(0)
		price_vector.append(p_high)

		demand_schedule = np.column_stack((demand_vector, price_vector))

		self.aggregate_demand.append([order['order_id'], demand_schedule])

		return demand_schedule

	def calc_supply(self, order):
		p_low = order['p_low']; p_high = order['p_high']; u_max = order['u_max']
		supply_vector = []
		price_vector = []
		# (will buy at u_max while p* < p_low)
		# for x in range(0, int(p_low)):
		supply_vector.append(0)
		price_vector.append(p_low)

		# p_low<= p* <= p_high
		for x in range(0, int((p_high - p_low) / Exchange._min_tick_size)):
			# price is every min tick increment between p_low and p_high
			price = p_low + x * Exchange._min_tick_size
			price_vector.append(price)
			supply_vector.append(u_max + ((price - p_high) / (p_high - p_low)) * u_max)

		# p* > p_high
		# for x in range(order['p_high'], int(order['p_high']*1.50)):
		supply_vector.append(u_max)
		price_vector.append(p_high)

		supply_schedule = np.column_stack((supply_vector, price_vector))

		self.aggregate_supply.append([order['order_id'], supply_schedule])

		return supply_schedule

	def calc_aggregate_demand(self):
		for order in self.book.bids:
			self.calc_demand(order)

	def calc_aggregate_supply(self):
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

	def get_price_range(self, is_demand=True):
		p_low = 10000000; p_high = 0
		if is_demand:
			for schedule in self.aggregate_demand:
				if schedule[1][0,1] < p_low:
					p_low = schedule[1][0,1]
				if schedule[1][-1,1] > p_high:
					p_high = schedule[1][-1,1]
		else:
			for schedule in self.aggregate_supply:
				if schedule[1][0,1] < p_low:
					p_low = schedule[1][0,1]
				if schedule[1][-1,1] > p_high:
					p_high = schedule[1][-1,1]
		return p_low, p_high

	def resize_schedules(self, new_length, u_max, is_demand=True):
		if is_demand:
			for schedule in self.aggregate_demand:
				sched_u_max = schedule[1][0,0]
				p_low = schedule[1][0,1]
				num_to_prepend = (u_max - sched_u_max) / Exchange._min_tick_size
				prepend_array = np.arange(p_low - num_to_prepend 
										* Exchange._min_tick_size, 
										p_low, Exchange._min_tick_size)
				# print(prepend_array, p_low)
				# prepend to_add number of sched_u_max to the schedules u_max
				
				# 
		else:
			pass

	def calc_crossing(self):
		pass

	def hold_batch(self):
		# holds a batch and then recursively calls its self after batch_time
		pass

	def _get_balance(self):
		return self.balance
