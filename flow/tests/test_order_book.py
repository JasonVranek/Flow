import sys
sys.path.append('../')
sys.path.append('../util')
from trader import Trader
from exceptions import InvalidMessageType, NoEntryFound, NoOrderToUpdate, NoOrderToCancel
from order_book import OrderBook

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
def active_bidder(default_trader):
	default_trader.enter_order('bid', 100, 80, 500, 2000)
	return default_trader

@pytest.fixture
def active_asker(default_trader):
	default_trader.enter_order('ask', 100, 80, 500, 2000)
	return default_trader

def test_default_trader_balance(default_trader):
	assert default_trader.balance == 0

def test_default_book(order_book):
	assert order_book.num_bids == 0

def test_cancel_order(default_trader):
	default_trader.cancel_order() == NoOrderToCancel

def test_enter_order(default_trader):
	default_trader.enter_order('bid', 100, 80, 500, 2000)
	assert default_trader.current_order == {'order_type': 'e', 
											'trader_type': 'bid', 
											'p_low': 80, 
											'p_high': 100, 
											'u_max': 500, 
											'q_max': 2000, 
											'funds': 0.0, 
											'order_id': 'account name'}

def test_update_order_on_default_trader(default_trader):
	assert default_trader.update_order(500, 400, 1000, 10000) == NoOrderToUpdate

def test_update_order_on_active_bidder(active_bidder):
	active_bidder.update_order(500, 400, 1000, 10000)
	assert active_bidder.current_order == {'order_type': 'u', 
										   'trader_type': 'bid', 
										   'p_low': 400, 
										   'p_high': 500, 
										   'u_max': 1000, 
										   'q_max': 10000, 
										   'funds': 0.0, 
										   'order_id': 'account name'}

def test_recieve_enter_bid(active_bidder, order_book):
	order_book.receive_message(active_bidder.current_order)
	assert order_book.message_queue.get() == {'order_type': 'e', 
											'trader_type': 'bid', 
											'p_low': 80, 
											'p_high': 100, 
											'u_max': 500, 
											'q_max': 2000, 
											'funds': 0.0, 
											'order_id': 'account name'}

def test_process_enter_bid(active_bidder, order_book):
	order_book.receive_message(active_bidder.current_order)
	order_book.process_messages()
	assert order_book.bids[active_bidder.current_order['order_id']] == {'order_type': 'e', 
											'trader_type': 'bid', 
											'p_low': 80, 
											'p_high': 100, 
											'u_max': 500, 
											'q_max': 2000, 
											'funds': 0.0, 
											'order_id': 'account name'}

def test_process_update_bid(active_bidder, order_book):
	order_book.receive_message(active_bidder.current_order)
	order_book.process_messages()

	active_bidder.update_order(500, 400, 1000, 10000)
	order_book.receive_message(active_bidder.current_order)
	order_book.process_messages()
	assert order_book.bids[active_bidder.current_order['order_id']] == {'order_type': 'u', 
										   'trader_type': 'bid', 
										   'p_low': 400, 
										   'p_high': 500, 
										   'u_max': 1000, 
										   'q_max': 10000, 
										   'funds': 0.0, 
										   'order_id': 'account name'}

def test_process_cancel_bid(active_bidder, order_book):
	order_book.receive_message(active_bidder.current_order)
	order_book.process_messages()

	active_bidder.cancel_order()
	order_book.receive_message(active_bidder.current_order)
	order_book.process_messages()
	assert order_book.bids == {}


def test_recieve_enter_ask(active_asker, order_book):
	order_book.receive_message(active_asker.current_order)
	assert order_book.message_queue.get() == {'order_type': 'e', 
											'trader_type': 'ask', 
											'p_low': 80, 
											'p_high': 100, 
											'u_max': 500, 
											'q_max': 2000, 
											'funds': 0.0, 
											'order_id': 'account name'}

def test_process_enter_ask(active_asker, order_book):
	order_book.receive_message(active_asker.current_order)
	order_book.process_messages()
	assert order_book.asks[active_asker.current_order['order_id']] == {'order_type': 'e', 
											'trader_type': 'ask', 
											'p_low': 80, 
											'p_high': 100, 
											'u_max': 500, 
											'q_max': 2000, 
											'funds': 0.0, 
											'order_id': 'account name'}

def test_process_update_ask(active_asker, order_book):
	order_book.receive_message(active_asker.current_order)
	order_book.process_messages()

	active_asker.update_order(500, 400, 1000, 10000)
	order_book.receive_message(active_asker.current_order)
	order_book.process_messages()
	assert order_book.asks[active_asker.current_order['order_id']] == {'order_type': 'u', 
										   'trader_type': 'ask', 
										   'p_low': 400, 
										   'p_high': 500, 
										   'u_max': 1000, 
										   'q_max': 10000, 
										   'funds': 0.0, 
										   'order_id': 'account name'}

def test_process_cancel_ask(active_asker, order_book):
	order_book.receive_message(active_asker.current_order)
	order_book.process_messages()

	active_asker.cancel_order()
	order_book.receive_message(active_asker.current_order)
	order_book.process_messages()
	assert order_book.asks == {}

def test_check_prices(active_bidder, order_book):
	# Send enter
	order_book.receive_message(active_bidder.current_order)
	order_book.process_messages()

	# Send update
	active_bidder.update_order(10000, 10, 1000, 10000)
	order_book.receive_message(active_bidder.current_order)
	order_book.process_messages()

	assert order_book.max_price == 10000 and order_book.min_price == 10


def test_find_new_prices(active_bidder, active_asker, order_book):
	# Send enter
	order_book.receive_message(active_bidder.current_order)
	order_book.receive_message(active_asker.current_order)
	order_book.process_messages()

	# Make the bidder have the highest prices:
	active_bidder.update_order(10000, 10, 1000, 10000)
	order_book.receive_message(active_bidder.current_order)
	order_book.process_messages()

	# Send cancel
	active_bidder.cancel_order()
	order_book.receive_message(active_bidder.current_order)
	order_book.process_messages()

	assert order_book.max_price == active_asker.current_order['p_high'] \
	and order_book.min_price == active_asker.current_order['p_low'] 

	







