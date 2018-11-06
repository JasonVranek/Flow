import sys
sys.path.append('../')
sys.path.append('../util')
sys.path.append('../data')
from exchange import Exchange
from pickle_helpers import read_file, get_books
import pytest
import pickle
import numpy as np


@pytest.fixture
def new_exchange():
	return Exchange('name', 'addr', 1000)

def test_batch(new_exchange):
	success = 0
	num_batches = 100
	num_error = 0
	for x in range(0, num_batches):
		try:
			bids, asks, result = get_books(x)
		except Exception as e:
			num_error += 1
			# print(e)
			continue
		new_exchange.bids = bids
		new_exchange.asks = asks
		new_exchange.min_price = result['min_price']
		new_exchange.max_price = result['max_price']

		new_exchange.calc_crossing()

		p = result['p*']
		print(f'Batch {x}, calculated: {new_exchange.clearing_price}, from data: {p}')
		if new_exchange.clearing_price == result['p*']:
			success += 1

		# assert new_exchange.clearing_price == result['p*']
	print(f'Succeeded {success} / {num_batches - num_error}')

# TODO, write a more iterative calc_cross alg and test if it also equals result['p*']

if __name__ == '__main__':
	ex = new_exchange()
	test_batch(ex)

