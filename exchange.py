from order_book import OrderBook

class Exchange(OrderBook):
	"""
		A market for trading with continuous scaled limit orders.

	Attributes:

	"""

	_batch_time = 5

	def __init__(self, name, address, balance, base_currency, desired_currency):
		OrderBook.__init__(self, base_currency, desired_currency)
		self.name = name
		self.address = address
		self.balance = balance
		self.supply = []
		self.demand = []


	def calc_demand(self):
		pass

	def calc_supply(self):
		pass

	def calc_crossing(self):
		pass

	def hold_batch(self):
		# holds a batch and then recursively calls its self after batch_time
		pass
