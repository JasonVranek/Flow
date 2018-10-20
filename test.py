from trader import Trader
from order_book import OrderBook

def test_book():
	book = OrderBook('ETH', 'BTC')
	return book

def test_trader(book):
	jason = Trader('account_name', 100)
	order = jason.new_order('buy', 101, 99, 500, 10000)
	cancel_order = jason.new_order('C', None, None, None , None)
	jason.describe()
	return jason


if __name__ == '__main__':
	book = test_book()
	import pdb; pdb.set_trace()
	jason = test_trader(book)

	book.receive_message(jason.current_order)

	book.process_messages()

	book.describe()
