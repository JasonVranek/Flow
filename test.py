from trader import Trader
from order_book import OrderBook
from exchange import Exchange


def test_book():
	book = OrderBook('ETH', 'BTC')
	return book

def test_trader(book):
	jason = Trader('jasons account', 100)
	order = jason.new_order('buy', 101, 99, 500, 10000)
	# cancel_order = jason.new_order('C', None, None, None , None)
	jason.describe()
	return jason


def main():
	# Create the exchange
	ex = Exchange('DEX', 'address', 1000)

	# Create the order book
	book = test_book()

	# Add the order book to the exchange
	ex.add_book(book)

	# Create a new trader
	jason = test_trader(ex)

	# Send an order to the exchange's order book
	ex.book.receive_message(jason.current_order)

	# Process any messages in the book's queue
	ex.book.process_messages()

	ex.book.describe()












if __name__ == '__main__':
	main()