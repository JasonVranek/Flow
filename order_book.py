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
		self.message_queue = []
		self.bids = {}
		self.asks = {}

	def receive_message(self, order):
		print('received message')
		# Check the order for errors

		# Add to message queue
		self.message_queue.append(order)

	def process_messages(self):
		# Check for any new messages in the message_queue
		for message in self.message_queue:
			print('processing message', message)
			if message['order_type'] == 'C':
				self.cancel_order(message)
				# Await response then delete from message_queue
				# self.message_queue.pop(message_id)
			else:
				message_id = message['order_id']
				self.add_order(message)
				# Await response then delete from message_queue
				# self.message_queue.pop(message_id)

		pass

	def cancel_order(self, order):
		print('trying to cancel order')
		message_id = order.order_id
		# Search book for order and delete it

		# delete it from bid/ask also
		pass

	def add_order(self, order):
		print('trying to add order')
		# Add the order to the book

		# Delete from bid/ask dict
		pass

	def query_book(self):
		return self.book

	def query_bids(self):
		pass

	def query_asks(self):
		pass

	def describe(self):
		print(self.base_currency, self.desired_currency, self.book, self.bids, self.asks)




