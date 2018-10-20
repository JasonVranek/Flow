class Trader(object):
	"""
		A market maker/taker participating in the Flow market.

	Attributes:
		account: A string that refers to the Trader's address
		balance: A float tracking the current balance of the Trader
		current_order: A dictionary containing the Trader's current order in the book
		order_count: an integer that increments per order sent
	"""
	def __init__(self, account, balance=0.0):
		"""Return a Trader object whose account number is 
		*account* and balance is *balance*."""
		self.account = account
		self.balance = balance
		self.current_order = {}
		self.order_count = 0

	def __str__(self):
		return self.account

	def update_balance(self, amount):
		if self.balance + amount < 0:
			raise RuntimeError('Insufficient funds to withdraw')
		self.balance += amount
		return self.balance

	def get_balance(self):
		return self.balance

	def get_current_order(self):
		return self.current_order

	def get_account(self):
		return self.account

	def new_order(self, order_type, p_high, p_low, u_max, q_max):
		"""Returns an order defined by the *order_type*."""
		if order_type is not 'C':
			self.current_order['q'] = q_max
			self.current_order['p_low'] = p_low
			self.current_order['p_high'] = p_high
			self.current_order['u_max'] = u_max

		self.current_order['order_type'] = order_type
		self.current_order['order_id'] = self.account + ' ' + str(self.order_count)
		self.order_count += 1

		return self.current_order

	def describe(self):
		print(self.get_account(), self.get_balance(), 
			  self.get_current_order())

