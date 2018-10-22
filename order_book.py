from exceptions import InvalidMessageType, NoEntryFound

class OrderBook(object):
	"""
		A continuous order book for the flow market.

	Attributes:
		
	"""

	def __init__(self, base_currency, desired_currency):
		self.num_bids = 0
		self.num_asks = 0
		self.book = []
		self.base_currency = desired_currency
		self.desired_currency = base_currency
		self.message_queue = []
		self.bids = []
		self.asks = []

	def receive_message(self, order):
		print('received message')
		# Check the order for errors

		# Add to message queue
		self.message_queue.append(order)

	def process_messages(self):
		# Check for any new messages in the message_queue
		try:
			for message in self.message_queue:
				print('processing message', message)
				order_type = msg['order_type']
				if order_type == 'C':
					self.cancel_order(message)
					# Await response then delete from message_queue
					# self.message_queue.pop(message_id)
				elif order_type == 'buy' or order_type == 'sell': 
					message_id = message['order_id']
					self.add_order(message)
					# Await response then delete from message_queue
					# self.message_queue.pop(message_id)
				else:
					raise InvalidMessageType

		except InvalidMessageType:
			print('Invalid Message Type')
			return 

	def add_order(self, order):
		print('Adding order')
		# Add the order to the book
		try:
			if order['order_type'] == 'buy':
				self.num_bids += 1
				self.bids.append(order)
			elif order['order_type'] == 'sell':
				self.num_asks += 1
				self.asks.append(order)
			else:
				raise InvalidMessageType
		except InvalidMessageType:
			print("triggered exception")
			return 

		self.book.append(order)

	def cancel_order(self, order):
		print('trying to cancel order')
		order_id = order['order_id']
		try: 
			# Search book for order and delete it
			order_type = self.delete_from_book(order_id)

			# Search bid/ask list for order and delete it
			if order_type == 'buy':
				self.delete_bid(order_id)
			elif order_type == 'sell':
				self.delete_ask(order_id)
			else:
				raise InvalidMessageType

		except InvalidMessageType:
			print('Invalid Message Type')
			return 

		except NoEntryFound:
			print('No order found to cancel')
			return
		
	def delete_from_book(self, order_id):
		for msg in self.book:
			if msg['order_id'] == order['order_id']:
				order_type = msg['order_type']
				self.book.remove(msg)
				return order_type
		return NoEntryFound

	def delete_bid(self, order_id):
		for msg in self.bids:
			if msg['order_id'] == order['order_id']:
				self.bids.remove(msg)
				self.num_bids -= 1
				return

	def delete_ask(self, order_id):
		for msg in self.asks:
			if msg['order_id'] == order['order_id']:
				self.asks.remove(msg)
				self.num_asks -= 1
				returm

	def query_book(self):
		return self.book

	def query_bids(self):
		return self.bids

	def query_asks(self):
		return self.asks

	def describe(self):
		print(self.base_currency, self.desired_currency, 
			  self.book, self.bids, self.asks, self.num_bids,
			  self.num_asks)



