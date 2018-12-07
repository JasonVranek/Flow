import numpy as np
import matplotlib.pyplot as plt
import pickle
from util.pickle_helpers import read_file
from exchange import Exchange
from graph import Graph
from trader import Trader
from payer import Payer


def setup_book(num_bids, num_asks):
	bids = {}
	asks = {}
	p_high = 110
	p_low = 90
	u_max = 250
	for x in range(0, num_asks):
		asker = Trader(f'asker{x}', 100000)
		asker.enter_order('ask', p_high, p_low, u_max, 10000)
		asks[asker.account] = asker.current_order

	for x in range(0, num_bids):
		p_low -= 10
		bidder = Trader(f'bidder{x}', 100000)
		bidder.enter_order('bid', p_high, p_low, u_max, 10000)
		bids[bidder.account] = bidder.current_order

	return bids, asks

def scenario_1():
	ex = Exchange('name', 'addr')
	bids, asks = setup_book(5, 5)
	min_p = 0
	max_p = 120
	tick_size = .1

	results  = ex.calc_crossing(min_p, max_p, tick_size, bids, asks, debug=False)
	c_p, c_r, bb, ba = results
	print(c_p, c_r, bb, ba)

	for id, bid in bids.items():
		print('bid', id, Payer.calc_demand(bid['p_low'], bid['p_high'], bid['u_max'], c_p))

	for id, ask in asks.items():
		print('ask', id, Payer.calc_supply(ask['p_low'], ask['p_high'], ask['u_max'], c_p))

	Graph.test_graph(min_p, max_p, tick_size, bids, asks, c_p, c_r)


def scenario_2():
	ex = Exchange('name', 'addr')
	bids = {}
	asks = {}
	min_p = 80
	max_p = 120
	tick_size = .1

	bidder1 = Trader('bidder1', 10000000)
	bidder1.enter_order('bid', 110, 90, 250, 10000)
	bids[bidder1.account] = bidder1.current_order

	asker1 = Trader('asker1', 100000)
	asker1.enter_order('ask', 110, 90, 250, 10000000)
	asks[asker1.account] = asker1.current_order

	mover_bid = Trader('mover_bid', 100000)
	mover_bid.enter_order('bid', 110, 90, 250, 10000)
	mover_bid.enter_order('bid', 110, 105, 500, 10000)
	bids[mover_bid.account] = mover_bid.current_order

	mover_ask = Trader('mover_ask', 100000)
	mover_ask.enter_order('ask', 110, 90, 250, 10000)
	asks[mover_ask.account] = mover_ask.current_order

	results  = ex.calc_crossing(min_p, max_p, tick_size, bids, asks, debug=False)
	c_p, c_r, bb, ba = results
	print(c_p, c_r, bb, ba)

	b1_shares = Payer.calc_demand(bidder1.current_order['p_low'], bidder1.current_order['p_high'], bidder1.current_order['u_max'], c_p)
	a1_shares = Payer.calc_supply(asker1.current_order['p_low'], asker1.current_order['p_high'], asker1.current_order['u_max'], c_p)
	move_bid_shares = Payer.calc_demand(mover_bid.current_order['p_low'], mover_bid.current_order['p_high'], mover_bid.current_order['u_max'], c_p)
	move_ask_shares = Payer.calc_supply(mover_ask.current_order['p_low'], mover_ask.current_order['p_high'], mover_ask.current_order['u_max'], c_p)
	print(f'bid1 shares: {b1_shares}')
	print(f'ask1 shares: {a1_shares}')
	print(f'mover_bid shares: {move_bid_shares}')
	print(f'mover_ask shares: {move_ask_shares}')

	Graph.test_graph(min_p, max_p, tick_size, bids, asks, c_p, c_r)


scenario_1()
# scenario_2()



def update_price(curr_price, agg_demand, agg_supply, order):
	if order['trader_type'] == 'bid':
		demand = Payer.calc_demand(order['p_low'], order['p_high'], order['u_max'], curr_price)  

	elif order['trader_type'] == 'ask':
		pass










# for num in range(0, 20):
# 	try:
# 		d = read_file(f'data/cross_fail_{num}')
# 		results  = ex.calc_crossing(d['min_p'], d['max_p'], d['tick_size'], d['bids'], d['asks'], debug=False)
# 		c_p, c_r, bb, ba = results
# 		print(c_p, c_r, bb, ba)

# 		# Graph.test_graph(d['min_p'], d['max_p'], d['tick_size'], d['bids'], d['asks'], c_p, c_r)
# 		Graph.test_graph(d['min_p'], d['max_p'], d['tick_size'], d['bids'], d['asks'], c_p, c_r)
# 	except Exception as e:
# 		pass

