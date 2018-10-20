from trader import Trader
from order_book import OrderBook
from exchange import Exchange


def test_book():
	book = OrderBook('ETH', 'BTC')
	return book

def test_trader(book):
	jason = Trader('account_name', 100)
	order = jason.new_order('buy', 101, 99, 500, 10000)
	cancel_order = jason.new_order('C', None, None, None , None)
	jason.describe()
	return jason


def main():
	exchange_ = Exchange('DEX', 'address', 1000, 'ETH', 'BTC')

	# book = test_book()

	jason = test_trader(exchange_)

	exchange_.receive_message(jason.current_order)

	exchange_.process_messages()

	# book.describe()












if __name__ == '__main__':
	main()