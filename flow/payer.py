class Payer():

	def find_shares_owed(bids, asks, clearing_price):
		bid_shares = {}
		ask_shares = {}
		sum_bids = 0
		sum_asks = 0
		for o_id, bid in bids.items():
			shares = Payer.calc_demand(bid['p_low'], bid['p_high'], bid['u_max'], clearing_price)
			bid_shares[o_id] = {'shares': shares,
							 'p*': clearing_price}
			sum_bids += shares


		for o_id, ask in asks.items():
			shares = Payer.calc_supply(ask['p_low'], ask['p_high'], ask['u_max'], clearing_price)
			ask_shares[o_id] = {'shares': shares,
							 'p*': clearing_price}
			sum_asks += shares

		# traders need currency 1 and 2
		return bid_shares, ask_shares, sum_bids, sum_asks

	def calc_supply(p_low, p_high, u_max, p):
		# Supply schedules add their u_max if pi > p_high
		if p > p_high:
			return float(u_max)
		# The price index is within their [p_low, p_high]
		elif p >= p_low and p <= p_high:
				return u_max + ((p - p_high) / (p_high - p_low)) * u_max
		else:
			return 0

	def calc_demand(p_low, p_high, u_max, p):
		# Demand schedules add their u_max if p_i < p_low
		if p < p_low:
				return float(u_max)
		# The price index is within their [p_low, p_high]
		elif p >= p_low and p <= p_high: 
			return u_max * ((p_high - p) / (p_high - p_low))
		else: 
			return 0

