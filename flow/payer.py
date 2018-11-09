class Payer():

	def find_shares_owed(bids, asks, clearing_price):
		bid_shares = {}
		ask_shares = {}
		sum_bids = 0
		sum_asks = 0
		for o_id, bid in bids.items():
			shares = Payer.calc_bid_shares(bid, clearing_price)
			bid_shares[o_id] = {'shares': shares,
							 'p*': clearing_price}
			sum_bids += shares


		for o_id, ask in asks.items():
			shares = Payer.calc_ask_shares(ask, clearing_price)
			ask_shares[o_id] = {'shares': shares,
							 'p*': clearing_price}
			sum_asks += shares

		# traders need currency 1 and 2
		return bid_shares, ask_shares, sum_bids, sum_asks

	def calc_bid_shares(bid, p_i):
		if p_i < bid['p_low']:
				return bid['u_max']

		# The price index is within their [p_low, p_high]
		elif p_i >= bid['p_low'] and p_i <= bid['p_high']: 
			return bid['u_max'] * ((bid['p_high'] - p_i) / (bid['p_high'] - bid['p_low']))

		else: 
			return 0

	def calc_ask_shares(ask, p_i):
			if p_i >= ask['p_low'] and p_i <= ask['p_high']:
				return ask['u_max'] + ((p_i - ask['p_high']) / (ask['p_high'] - ask['p_low'])) * ask['u_max']

			# Supply schedules add their u_max if pi > p_high
			elif p_i > ask['p_high']:
				return ask['u_max']

			else:
				return 0