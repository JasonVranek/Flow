from trader import Trader
from order_book import OrderBook
from exchange import Exchange
from exceptions import InvalidMessageType, NoEntryFound

from order_book_backup import TestOrderBook

import pytest
import random

# run with pytest test.py
@pytest.fixture
def default_trader():
	'''Returns a trader object with balance 0.0'''
	return Trader('account name')

@pytest.fixture
def order_book():
	'''Returns an order book object'''
	return OrderBook('ETH', 'BTC')

@pytest.fixture
def empty_exchange():
	'''Returns an exchange object with no order book'''
	return Exchange('DEX', 'address')

@pytest.fixture
def exchange(empty_exchange, order_book):
	'''Returns an exchange object with an order book'''
	empty_exchange.book = order_book
	return empty_exchange

@pytest.fixture
def bid():
	'''Returns a bid order to be used with a trader'''
	return ['buy', 101, 99, 500, 10000]

@pytest.fixture
def ask():
	'''Returns an ask order to be used with a trader'''
	return ['sell', 100, 98, 400, 10000]

@pytest.fixture
def cancel():
	'''Returns a cancel order to be used with a trader'''
	return ['C', None, None, None, None]

@pytest.fixture
def invalid_message():
	'''Returns an invalid order to be used with a trader'''
	return ['invalid', 101, 99, 500, 10000]

@pytest.fixture
def traders():
	"""Creates 4 * number_per_type traders of equal order type distribution  """
	number_per_type = 10000
	traders = []
	orders = []
	order_type = ['buy', 'sell', 'C', 'invalid']
	for x in range(0, 4):
		for y in range(0, number_per_type):
			orders.append(order_type[x])
			
	for i in range(0, 4 * number_per_type):
		name = f'Trader{i}'
		trader = Trader(name, random.randint(50, 300))
		
		trader.new_order(orders[i], 		# 'buy', 'sell', 'c', 'invalid'
							random.randint(100, 110), 	# p_high
							random.randint(90, 100),  	# p_low
							random.randint(0, 500), 		# u_max
							random.randint(1000, 2000))	# q_max
		traders.append(trader)
	return traders

def test_default_trader_balance(default_trader):
	assert default_trader.balance == 0

def test_new_order(default_trader, bid):
	order = default_trader.new_order(*bid)
	assert order == {'p_high': 101, 'p_low': 99, 
					'u_max': 500, 'q': 10000, 'order_type': 
					'buy', 'order_id': f'{default_trader.account} 1'}

def test_send_bid(default_trader, bid, exchange):
	default_trader.new_order(*bid)
	exchange.get_order(default_trader.current_order)
	assert exchange.book.message_queue[0] == default_trader.current_order

def test_send_ask(default_trader, ask, exchange):
	default_trader.new_order(*ask)
	exchange.get_order(default_trader.current_order)
	assert exchange.book.message_queue[0] == default_trader.current_order

def test_send_cancel(default_trader, cancel, exchange):
	default_trader.new_order(*cancel)
	exchange.get_order(default_trader.current_order)
	assert exchange.book.message_queue[0] == default_trader.current_order

def test_send_incorrect_order_type(default_trader, bid, exchange):
	bid[0] = 'wrong'
	default_trader.new_order(*bid)
	exchange.get_order(default_trader.current_order)
	assert exchange.book.message_queue[0] == default_trader.current_order

def test_process_bid(default_trader, bid, exchange):
	default_trader.new_order(*bid)
	exchange.get_order(default_trader.current_order)
	exchange.book.process_messages()
	assert exchange.book.book[0] == default_trader.current_order

def test_process_ask(default_trader, ask, exchange):
	default_trader.new_order(*ask)
	exchange.get_order(default_trader.current_order)
	exchange.book.process_messages()
	assert exchange.book.book[0] == default_trader.current_order

def test_process_cancel(default_trader, cancel, exchange):
	default_trader.new_order(*cancel)
	exchange.get_order(default_trader.current_order)
	exchange.book.process_messages()
	assert len(exchange.book.book) == 0

def test_process_incorrect_order_type(default_trader, invalid_message, exchange):
	default_trader.new_order(*invalid_message)
	exchange.get_order(default_trader.current_order)
	exchange.book.process_messages()
	assert len(exchange.book.book) == 0

def test_process_many_orders(traders, exchange):
	for trader in traders:
		exchange.get_order(trader.current_order)

	while len(exchange.book.message_queue) > 0:
		exchange.book.process_messages()
	print(len(exchange.book.book), exchange.book.num_asks, exchange.book.num_bids)
	assert (len(exchange.book.book) == 20000 \
			and exchange.book.num_asks == 10000 \
			and exchange.book.num_bids == 10000)







