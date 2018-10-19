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

		def create_order(self, buy_sell, q_max, p_low, p_high, u_max, book):
			if self.current_order is not None:
				self.cancel_order(book)
			self.order_count += 1
			self.current_order['buy_sell'] = buy_sell
			self.current_order['q'] = q_max
			self.current_order['p_low'] = p_low
			self.current_order['p_high'] = p_high
			self.current_order['u_max'] = u_max
			self.current_order['order_id'] = str(self.account 
												+ ' '
												+ self.order_count)
			self._send_order(order, book)
			return self.current_order

		def cancel_order(self, book):
			"""Delete the Trader's current order and submit an
			order to cancel to the book"""
			cancel_order = {'type': 'C', 'order_id': self.current_order['order_id'],
							'account': self.account}
			self.current_order = {}
			self._send_order(cancel_order, book)

		def _send_order(self, order, book):
			book.receive_message(order)
			return order


