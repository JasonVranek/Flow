class OrderBook(object):
	"""
		A continuous order book for the flow market.

	Attributes:
		
	"""

	def __init__(self, base_currency, desired_currency):
		self.num_bids = 0
		self.num_asks = 0
		self.book = {}
		self.base_currency = desired_currency
		self.desired_currency = base_currency
		self.message_queue = {}
		self.bids = {}
		self.asks = {}

	def receive_message(self, order):
		# Check the order for errors

		# Add to message queue
		self.message_queue.update(order)

	def process_messages(self):
		# Check for any new messages in the message_queue
		for message in self.message_queue:
			if message.type is 'C':
				message_id = order.order_id
				self.cancel_order(order)
				# Await response then delete from message_queue
				self.message_queue.pop(message_id)
			else:
				message_id = order.order_id
				self.add_order(order)
				# Await response then delete from message_queue
				self.message_queue.pop(message_id)

		pass

	def cancel_order(self, order):
		message_id = order.order_id
		# Search book for order and delete it

		# delete it from bid/ask also
		pass

	def add_order(self, order):
		# Add the order to the book

		# Delete from bid/ask dict
		pass

	def query_book(self):
		return self.book

	def query_bids(self):
		pass

	def query_asks(self):
		pass




