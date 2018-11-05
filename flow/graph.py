import matplotlib.pyplot as plt, mpld3
from matplotlib.animation import FuncAnimation
from matplotlib.animation import TimedAnimation
import numpy as np
import math
import time

class Graph():

	def __init__(self, exchange):
		self.exchange = exchange
		self.fig = plt.figure()
		self.ax = self.fig.add_subplot(111)

	def add_titles(self):
		plt.title(f'Total of batch {self.exchange.batch_num}')
		plt.xlabel(f'(Price {self.exchange.book.base_currency}/{self.exchange.book.desired_currency})')
		plt.ylabel(f'(Quantity Traded (shares/batch)')

	def graph_aggregates(self):
		zoom = 5
		self.ax.clear()
		self.add_titles()
		sup_array = []
		dem_array = []
		p_array = []
		max_price = self.exchange.max_price
		min_price = self.exchange.min_price
		for x in range(math.floor(min_price - 10), math.floor(max_price + 10)):
			dem, sup = self.exchange.calc_aggs(x)
			dem_array.append(dem)
			sup_array.append(sup)
			p_array.append(x)

		self.ax.plot(p_array, dem_array, 'b')
		self.ax.plot(p_array, sup_array, 'r')

		# plot horizontal clearing rate line
		cr = self.exchange.clearing_rate
		cp = self.exchange.clearing_price
		self.ax.plot([0, cp], [cr, cr], 'g')

		# plot vertical clearing price line
		self.ax.plot([cp, cp], [0, cr], 'g')
		
		nice_cp = self.exchange.nice_precision(cp)
		nice_cr = self.exchange.nice_precision(cr)
		nice_bb = self.exchange.nice_precision(self.exchange.best_bid)
		nice_ba = self.exchange.nice_precision(self.exchange.best_ask)
		num_bids = self.exchange.book.num_bids
		num_asks = self.exchange.book.num_asks

		text_str = 'p*=%.2f\nu*=%.2f\ndem=%.2f\nsup=%.2f\nnum_bids=%d\nnum_ask=%d'%(nice_cp, nice_cr, nice_bb, nice_ba, num_bids, num_asks)

		plt.text(.75, .4, text_str, transform=plt.gcf().transFigure)

		plt.subplots_adjust(right=0.7)

	def animate(self, func):
		# Recalls the run_batch function every batch_time
		ani = FuncAnimation(self.fig, func, frames=60, interval=self.exchange._batch_time * 1000)
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






