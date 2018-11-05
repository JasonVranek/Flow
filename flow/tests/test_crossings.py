import sys
sys.path.append('../')
sys.path.append('../util')
sys.path.append('../data')
from exchange import Exchange
from pickle_helpers import read_file, get_books
import pytest
import pickle

@pytest.fixture
def new_exchange():
	return Exchange('name', 'addr', 1000)

def test_batch(new_exchange):
	for x in range(0, 10):
		bids, asks, result = get_books(x)
		new_exchange.bids = bids
		new_exchange.asks = asks
		new_exchange.min_price = result['min_price']
		new_exchange.max_price = result['max_price']

		new_exchange.calc_crossing()

		p = result['p*']
		print(f'Batch {x}, calculated: {new_exchange.clearing_price}, from data: {p}')

		# assert new_exchange.clearing_price == result['p*']

if __name__ == '__main__':
	ex = new_exchange()
	test_batch(ex)

