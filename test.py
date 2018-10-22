from trader import Trader
from order_book import OrderBook
from exchange import Exchange

import random
import time

def test_book():
	book = OrderBook('ETH', 'BTC')
	return book


def test_trader(book):
	jason = Trader('jasons account', 100)
	order = jason.new_order('buy', 101, 99, 500, 10000)
	# cancel_order = jason.new_order('C', None, None, None, None)
	jason.describe()
	return jason


def setup_traders():
	num_traders = 5
	traders = []
	order_type = ['buy', 'sell', 'C', 'poop']
	for i in range(0, num_traders):
		name = 'Trader' + str(i)
		trader = Trader(name, random.randint(50, 300))
		trader.new_order(random.choice(order_type), 		# 'buy', 'sell', 'c'
							random.randint(100, 110), 	# p_high
							random.randint(90, 100),  	# p_low
							random.randint(0, 500), 		# u_max
							random.randint(1000, 2000))	# q_max
		traders.append(trader)
		print(trader.current_order)
	return traders


def main():
	# Create the exchange
	ex = Exchange('DEX', 'address', 1000)

	# Create the order book
	book = test_book()

	# Add the order book to the exchange
	ex.add_book(book)

	# Create a new trader
	traders = setup_traders()

	# Send an order to the exchange's order book
	for trader in traders:
		ex.book.receive_message(trader.current_order)

	print('Received:', len(ex.book.message_queue), 'messages')

	# Process any messages in the book's queue
	ex.book.process_messages()

	ex.book.pretty_book()

	print('TESTING CANCEL')
	for trader in traders:
		trader.new_order('C', None, None, None, None)
		ex.book.receive_message(trader.current_order)
	ex.book.process_messages()

	ex.book.pretty_book()



	












if __name__ == '__main__':
	main()