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

	def add_book(self, book):
		self.book = book

	def get_order(self, order):
		self.book.receive_message(order)

	def _get_shape(self, p_low, p_high):
		length =  (p_high - p_low) / Exchange._min_tick_size
		return (length, length)

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
		# for x in range(order['p_high'], int(order['p_high']*1.50)):
		demand_vector.append(0)
		price_vector.append(p_high)

		return np.column_stack((demand_vector, price_vector))

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

		return np.column_stack((supply_vector, price_vector))

	def calc_crossing(self):
		pass

	def hold_batch(self):
		# holds a batch and then recursively calls its self after batch_time
		pass

	def _get_balance(self):
		return self.balance
