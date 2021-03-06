import matplotlib.pyplot as plt, mpld3
from matplotlib.animation import FuncAnimation
from matplotlib.animation import TimedAnimation
from payer import Payer
import numpy as np
import math
import time

class Graph():

	def get_aggs(bids, asks, p):
		agg_demand = 0
		agg_supply = 0
		for o_id, bid in bids.items():
			agg_demand += Payer.calc_demand(bid['p_low'], bid['p_high'], bid['u_max'], p)

		for o_id, ask in asks.items():
			agg_supply += Payer.calc_supply(ask['p_low'], ask['p_high'], ask['u_max'], p)
		
		return agg_demand, agg_supply

	def test_graph(min_p, max_p, tick_size, bids, asks, cp, cr):
		fig = plt.figure()
		ax = fig.add_subplot(111)
		sup_array = []
		dem_array = []
		p_array = []

		# for price in range(math.floor(min_p), math.ceil(max_p)):
		for price in range(math.floor(min_p / tick_size), math.ceil(max_p / tick_size)):
			dem, sup = Graph.get_aggs(bids, asks, price * tick_size)
			dem_array.append(dem)
			sup_array.append(sup)
			p_array.append(price * tick_size)

		ax.plot(p_array, dem_array, 'b')
		ax.plot(p_array, sup_array, 'r')

		if cp > 0 and cr > 0:
			# plot horizontal clearing rate line
			ax.plot([min_p, cp], [cr, cr], 'g')

			# plot vertical clearing price line
			ax.plot([cp, cp], [0, cr], 'g')


		text_str = 'p*=%f  u*=%f'%(cp, cr)
		plt.text(.75, .5, text_str, transform=plt.gcf().transFigure)
		plt.subplots_adjust(right=0.7)
		plt.show()


	def __init__(self, exchange):
		self.exchange = exchange
		self.fig = plt.figure()
		self.ax = self.fig.add_subplot(111)

	def add_titles(self):
		plt.title(f'Total of batch {self.exchange.batch_num}')
		plt.xlabel(f'(Price {self.exchange.book.base_currency}/{self.exchange.book.desired_currency})')
		plt.ylabel(f'(Volume ({self.exchange.book.desired_currency}/batch)')

	def graph_aggregates(self):
		zoom = 5
		self.ax.clear()
		self.add_titles()
		sup_array = []
		dem_array = []
		p_array = []
		max_price = self.exchange.max_price
		min_price = self.exchange.min_price
		cr = self.exchange.clearing_rate
		cp = self.exchange.clearing_price
		for price in range(math.floor(min_price), math.ceil(max_price)):
		# for price in range(math.floor((cp - 1) / self.exchange._min_tick_size), math.ceil((cp + 1) / self.exchange._min_tick_size)):
			dem, sup = Graph.get_aggs(self.exchange.bids, self.exchange.asks, price)
			dem_array.append(dem)
			sup_array.append(sup)
			p_array.append(price)

		self.ax.plot(p_array, dem_array, 'b')
		self.ax.plot(p_array, sup_array, 'r')

		if cp > 0 and cr > 0:
			# plot horizontal clearing rate line
			self.ax.plot([min_price, cp], [cr, cr], 'g')

			# plot vertical clearing price line
			self.ax.plot([cp, cp], [0, cr], 'g')
		
		nice_cp = self.exchange.nice_precision(cp)
		nice_cr = self.exchange.nice_precision(cr)
		nice_bb = self.exchange.nice_precision(self.exchange.best_bid)
		nice_ba = self.exchange.nice_precision(self.exchange.best_ask)
		num_bids = self.exchange.book.num_bids
		num_asks = self.exchange.book.num_asks

		# text_str = 'p*=%.2f\nu*=%.2f\ndem=%.2f\nsup=%.2f\nnum_bids=%d\nnum_ask=%d'%(nice_cp, nice_cr, nice_bb, nice_ba, num_bids, num_asks)
		# plt.text(.75, .4, text_str, transform=plt.gcf().transFigure)

		text_str = 'p*=%.2f  u*=%.2f'%(nice_cp, nice_cr)
		text_str2 = 'dem=%.2f  sup=%.2f'%(nice_bb, nice_ba)
		text_str3 = 'num_bids=%d  num_ask=%d'%(num_bids, num_asks)

		plt.text(.75, .5, text_str, transform=plt.gcf().transFigure)
		plt.text(.75, .45, text_str2, transform=plt.gcf().transFigure)
		plt.text(.75, .4, text_str3, transform=plt.gcf().transFigure)

		plt.subplots_adjust(right=0.7)

	def animate(self, func):
		# Recalls the run_batch function every batch_time
		ani = FuncAnimation(self.fig, func, frames=30, interval=self.exchange._batch_time * 1000)
		# ani.save('animation.html', writer="avconv", codec="libx264")
		plt.show()

	def pause(self):
		plt.pause(1)

	def display(self):
		plt.show()

	def graph_as_html(self):
		return mpld3.fig_to_html(self.fig)

	def redraw(self):
		self.fig.clear()
		# self.ax.clear()

	def close(self):
		plt.close()

	# def get_aggs(self, bids, asks, p):
	# 	agg_demand = 0
	# 	agg_supply = 0
	# 	for o_id, bid in bids.items():
	# 		agg_demand += Payer.calc_demand(bid['p_low'], bid['p_high'], bid['u_max'], p)

	# 	for o_id, ask in asks.items():
	# 		agg_supply += Payer.calc_supply(ask['p_low'], ask['p_high'], ask['u_max'], p)
		
	# 	return agg_demand, agg_supply








