from trader import Trader
from order_book import OrderBook
from exchange import Exchange
from exceptions import InvalidMessageType, NoEntryFound
import pytest

# run with pytest test.py
@pytest.fixture
def default_trader():
	return Trader('account name')

@pytest.fixture
def order_book():
	return OrderBook('ETH', 'BTC')

@pytest.fixture
def empty_exchange():
	return Exchange('DEX', 'address')

@pytest.fixture
def exchange(empty_exchange, order_book):
	empty_exchange.book = order_book
	return empty_exchange

@pytest.fixture
def bid():
	return ['buy', 101, 99, 500, 10000]

@pytest.fixture
def ask():
	return ['sell', 100, 98, 400, 10000]

@pytest.fixture
def cancel():
	return ['c', None, None, None, None]

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
	

def test_process_bid():
	pass

def test_process_ask():
	pass








