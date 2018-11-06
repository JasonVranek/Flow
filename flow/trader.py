from util.exceptions import NoOrderToUpdate, NoOrderToCancel

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
			self.order_count += 1

		self.current_order['order_type'] = order_type
		self.current_order['order_id'] = f'{self.account}:{self.order_count}'

		return self.current_order

	def enter_order(self, trader_type, p_high, p_low, u_max, q_max):
		new_order = {}
		new_order['order_type'] = 'e'
		new_order['trader_type'] = trader_type
		new_order['p_low'] = p_low
		new_order['p_high'] = p_high
		new_order['u_max'] = u_max
		new_order['q_max'] = q_max
		new_order['funds'] = self.balance
		new_order['order_id'] = self.account
		self.current_order = new_order

	def cancel_order(self):
		new_order = {}
		new_order['order_type'] = 'c'
		new_order['trader_type'] =  self.current_order.get('trader_type', None)
		if new_order['trader_type'] == None:
			print('Error, no order to cancel!')
			return NoOrderToCancel
		new_order['p_low'] = self.current_order.get('p_low')
		new_order['p_high'] = self.current_order.get('p_high')
		new_order['u_max'] = self.current_order.get('u_max')
		new_order['q_max'] = self.current_order.get('q_max')
		new_order['order_id'] = self.account
		self.current_order = new_order

	def update_order(self, p_high, p_low, u_max, q_max):
		new_order = {}
		new_order['order_type'] = 'u'
		new_order['trader_type'] =  self.current_order.get('trader_type', None)
		if new_order['trader_type'] == None:
			print('Error, no order to update!')
			return NoOrderToUpdate
		new_order['p_low'] = p_low
		new_order['p_high'] = p_high
		new_order['u_max'] = u_max
		new_order['q_max'] = q_max
		new_order['funds'] = self.balance
		new_order['order_id'] = self.account
		self.current_order = new_order

	def describe(self):
		print(self.get_account(), self.get_balance(), 
			  self.get_current_order())

