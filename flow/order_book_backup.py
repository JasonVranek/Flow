from exceptions import InvalidMessageType, NoEntryFound, InvalidMessageParameter
from copy import deepcopy

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
		self.new_messages = []
		self.max_price = 0
		self.min_price = 100000

	def receive_message(self, order):
		# Make a deepcopy of the order
		copied_order = deepcopy(order)
		# Add to message queue
		self.message_queue.append(copied_order)

	def process_messages(self):
		# Check for any new messages in the message_queue
		for msg in self.message_queue:
			#print('processing message', msg)
			try:
				order_type = msg['order_type']
				if order_type == 'C':
					old_order_type = self.cancel_order(msg)
					self.message_queue.remove(msg)
					# Append 'buy' or 'sell' to indicate where to cancel from in exchange
					msg['old_type'] = old_order_type
					self.new_messages.append(msg)
				elif order_type == 'buy' or order_type == 'sell': 
					message_id = msg['order_id']
					self.add_order(msg)
					self.message_queue.remove(msg)
				else:
					# Remove invalid messages from the queue
					self.message_queue.remove(msg)
					raise InvalidMessageType

			except InvalidMessageType:
				pass
				#print('Invalid Message Type', msg)

	def is_update(self, order):
		# Returns old order if the trader has an order already in the book
		cur_trader = order['order_id'].split(':')
		for entry in self.book:
			o_id = entry['order_id']
			entry_data = o_id.split(':')
			# If the trader already has an order in the book
			if cur_trader[0] == entry_data[0]:
				print(f'{cur_trader[0]} is trying to update from {entry} to {order}')
				if cur_trader[1] < entry_data[1]:
					# Trader submitted an order with lower nonce
					print('Error, trying to sending old order_id!')
					return False
				# Return the old order so it can be easily cancelled
				return entry
		return False

	def implicit_cancel_msg(self, order, old_order_type):
		# Create a cancel message from the order
		return {'order_type': 'C','order_id': order['order_id'], 
				'old_type': old_order_type, 'p_low': order['p_low'],
				'p_high': order['p_high'], 'u_max': order['u_max'],
				'q': order['q']}
			 
	def add_order(self, order):
		#print('Adding order')
		try:
			# Check the order for correct parameters
			if self.check_order_params(order) == InvalidMessageParameter:
				raise InvalidMessageParameter

			# Check if this message is updating a previous one
			old_order = self.is_update(order)
			if old_order is not False:
				# Delete old message from book/bids/ask
				old_order_type = self.cancel_order(old_order)
				# Create and send implicit cancel message to exchange
				cancel_msg = self.implicit_cancel_msg(old_order, old_order_type)
				self.new_messages.append(cancel_msg)

			# Proceed to process the new message
			if order['order_type'] == 'buy':
				self.num_bids += 1
				self.book.append(order)
				self.bids.append(order)
				self.new_messages.append(order)
			elif order['order_type'] == 'sell':
				self.num_asks += 1
				self.book.append(order)
				self.asks.append(order)
				self.new_messages.append(order)
			else:
				raise InvalidMessageType

		except InvalidMessageType:
			print("triggered InvalidMessageType")
		except InvalidMessageParameter:
			print('trigger InvalidMessageParameter')
			 

	def cancel_order(self, order):
		#print('trying to cancel order')
		# The order_id from cancel will correspond to the current buy/sell in book
		order_id = order['order_id']
		try: 
			# Search book for order and delete it
			old_order_type = self.delete_from_book(order_id)
			# Delete it from the new_messages queue if exchange hasnt processed
			# TODOTODOTODOTODOTO

			# Search bid/ask list for order and delete it
			if old_order_type == 'buy':
				self.delete_bid(order_id)
			elif old_order_type == 'sell':
				self.delete_ask(order_id)
			elif old_order_type == NoEntryFound:
				raise NoEntryFound
			else:
				raise InvalidMessageType

		except InvalidMessageType:
			print('Invalid Message Type')

		except NoEntryFound:
			print('No order found to cancel')

		return old_order_type
		
	def delete_from_book(self, order_id):
		for msg in self.book:
			if msg['order_id'] == order_id:
				order_type = msg['order_type']
				self.book.remove(msg)
				# Return the order_type so we can delete from bid/ask list
				#print('deleted from book: ', msg)
				return order_type
		return NoEntryFound

	def delete_bid(self, order_id):
		for msg in self.bids:
			if msg['order_id'] == order_id:
				self.bids.remove(msg)
				self.num_bids -= 1
				#print('deleted bid: ', msg)
				return True
		return NoEntryFound

	def delete_ask(self, order_id):
		for msg in self.asks:
			if msg['order_id'] == order_id:
				self.asks.remove(msg)
				self.num_asks -= 1
				#print('deleted ask: ', msg)
				return True
		return NoEntryFound

	def check_prices(self, p_low, p_high, is_update):
		if is_update:
			if p_low == self.min_price:
				print('Updating min_price')
			elif p_high == self.max_price:
				print('Updating max_price')

		else:
			if p_low < self.min_price:
				self.min_price = p_low
				print('New min_price')
			elif p_high > self.max_price:
				self.max_price = p_high
				print('New max_price')
		

	def check_order_params(self, order):
		if not isinstance(order['q'], int):
			return InvalidMessageParameter
		elif not isinstance(order['p_low'], int):
			return InvalidMessageParameter
		elif not isinstance(order['p_high'], int):
			return InvalidMessageParameter
		elif not isinstance(order['u_max'], int):
			return InvalidMessageParameter
		return True

	def query_book(self):
		return self.book

	def query_bids(self):
		return self.bids

	def query_asks(self):
		return self.asks

	def describe(self):
		print(self.base_currency, self.desired_currency, 
			  self.book, self.num_bids,
			  self.num_asks)

	def pretty_book(self):
		print()
		print(f'Order Book({self.base_currency} -> {self.desired_currency})')
		print(f'Entries: {len(self.book)}, Bids: {self.num_bids}, Asks: {self.num_asks}')
		# print('Entries: ', len(self.book), ', Bids: ', self.num_bids, ', Asks: ', self.num_asks)
		for order in self.book:
			print(order)
		print()



