from exceptions import InvalidMessageType, NoEntryFound, InvalidMessageParameter
from copy import deepcopy
from queue import Queue

class OrderBook(object):
	"""
		A continuous order book for the flow market.

	Attributes:
		
	"""

	def __init__(self, base_currency, desired_currency):
		self.num_bids = 0
		self.num_asks = 0
		self.base_currency = desired_currency
		self.desired_currency = base_currency
		self.bids = {}
		self.asks = {}
		self.max_price = 0
		self.min_price = 100000000
		self.message_queue = Queue()

	def receive_message(self, order):
		# Make a deepcopy of the order
		copied_order = deepcopy(order)
		# Add to message queue
		self.message_queue.put(copied_order)

	def process_messages(self):
		while not self.message_queue.empty():
			# Pop msg from message queue
			msg = self.message_queue.get()
			#print('processing message', msg)
			try:
				order_type = msg['order_type']
				if order_type == 'c':
					# Delete the message from book's queue
					# Cancel the order and check if the min/max prices changed
					old_p_low, old_p_high = self.cancel_order(msg)
					if old_p_low >= 0 or old_p_high >= 0:
						self.check_prices(old_p_low, old_p_high, 'c')
					else:
						print('Couldnt cancel order', msg)

				elif order_type == 'u':
					# Check if this update changes min/max
					self.check_prices(msg['p_low'], msg['p_high'], 'u')
					print(f'in u: msg: {msg}')

					# need to update the bid/ask in the respective book
					old_p_low, old_p_high = self.update_order(msg)
					if old_p_low >= 0 or old_p_high >= 0:
						# If I updated from [80, 120] -> [90, 110], and self.min_price = 80,
						# Then I would have to update self.min_price since my old price is 
						# no longer valid. 
						self.check_prices(old_p_low, old_p_high, 'c')
					else:
						print('Couldnt update order')

				elif order_type == 'e':
					# Check if this new message contains min/max price
					self.check_prices(msg['p_low'], msg['p_high'], 'e')

					# Add the message to the respective books
					self.add_order(msg)
				else:
					# Remove invalid messages from the queue
					# self.message_queue.remove(msg)
					raise InvalidMessageType

			except InvalidMessageType:
				pass
				#print('Invalid Message Type', msg)

	def add_order(self, order):
		try:
			# Proceed to process the new message
			if order['trader_type'] == 'bid':
				self.num_bids += 1
				# Add to dictionary
				self.bids[order['order_id']] = order
			elif order['trader_type'] == 'ask':
				self.num_asks += 1
				# Add to dictionary
				self.asks[order['order_id']] = order
			else:
				raise InvalidMessageType

		except InvalidMessageType:
			print("triggered InvalidMessageType")
		except Exception as e:
			print(e)
			 

	def cancel_order(self, order):
		# Search bid/ask list for order and delete it
		if order['trader_type'] == 'bid':
			return self.delete_bid(order['order_id'])
		elif order['trader_type'] == 'ask':
			return self.delete_ask(order['order_id'])

	def update_order(self, order):
		# Finds bid/ask in the respective book and update params
		order_id = order['order_id']
		if order['trader_type'] == 'bid':
			if order_id in self.bids:
				bid = self.bids[order_id] 
				# Save old prices
				old_p_low = bid['p_low']
				old_p_high = bid['p_high']

				# Make updates:
				self.bids[order_id] = order

				# Return old prices for price check
				return old_p_low, old_p_high
		else:
			if order_id in self.asks:
				ask = self.asks[order_id]
				# Save old prices
				old_p_low = ask['p_low']
				old_p_high = ask['p_high']
				
				# Make updates:
				self.asks[order_id] = order
				
				# Return old prices for price check
				return old_p_low, old_p_high

		# TODO let them update from bid <-> ask 

		print('UHOH COULDNT FIND AN ORDER TO UPDATE!', order)	
		return -1, -1
		
	def delete_bid(self, order_id):
		try:
			bid = self.bids.pop(order_id)
			self.num_bids -= 1
			return bid['p_low'], bid['p_high']
		except KeyError:
			print('Bid not found to delete! ', order_id)
			self.pretty_book()
			# exit(1)
			return -1, -1

	def delete_ask(self, order_id):
		try:
			ask = self.asks.pop(order_id)
			self.num_asks -= 1
			return ask['p_low'], ask['p_high']
		except KeyError:
			print('Ask not found to delete! ', order_id)
			self.pretty_book()
			# exit(1)
			return -1, -1

	def check_prices(self, p_low, p_high, order_type):
		if order_type == 'C':
			if p_low == self.min_price or p_high == self.max_price:
				# print('Cancelled previous min_price/max_price')
				self.min_price, self.max_price = self.find_new_prices()

		else:
			if p_low < self.min_price:
				self.min_price = p_low
				# print('New min_price ', p_low)
			if p_high > self.max_price:
				self.max_price = p_high
				# print('New max_price ', p_high)

	def find_new_prices():
		new_max = 0
		new_min = 100000000
		# look at dictionary values
		for o_id, order in self.bids.items():
			if order['p_high'] > new_max:
				new_max = order['p_high']
			if order['p_low'] < new_min:
				new_min = order['p_low']

		for o_id, order in self.asks.items():
			if order['p_high'] > new_max:
				new_max = order['p_high']
			if order['p_low'] < new_min:
				new_min = order['p_low']

		return new_min, new_max

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
		print(f'Number of bids: {self.num_bids}, Number of Asks: {self.num_asks}')
		print('BIDS')
		for order_id in self.bids:
			print(f'{order_id}: {self.bids[order_id]}')

		print()
		print('ASKS')
		for order_id in self.asks:
			print(f'{order_id}: {self.asks[order_id]}')
		print()



