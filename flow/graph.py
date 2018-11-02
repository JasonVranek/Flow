import matplotlib.pyplot as plt, mpld3
import numpy as np
import math

class Graph():

	def __init__(self):
		self.exchange = object

	def set_exchange(self, exchange):
		self.exchange = exchange

	def test_graph(self, figure_num):
		plt.figure(figure_num)

		sup_array = []
		dem_array = []
		p_array = []
		for x in range(math.floor(self.exchange.min_price - 10), math.floor(self.exchange.max_price + 10)):
			dem, sup = self.exchange.calc_agg(x)
			dem_array.append(dem)
			sup_array.append(sup)
			p_array.append(x)

		plt.plot(p_array, dem_array)
		plt.plot(p_array, sup_array)

		# plot horizontal clearing rate line
		plt.plot([self.exchange.min_price - 10, self.exchange.clearing_price], [self.exchange.clearing_rate, self.exchange.clearing_rate], 'g')

		# plot vertical clearing price line
		plt.plot([self.exchange.clearing_price, self.exchange.clearing_price], [0, self.exchange.clearing_rate], 'g')
		
		plt.title(f'Total of batch {self.exchange.batch_num}')

		nice_cp = self.exchange.nice_precision(self.exchange.clearing_price)
		nice_cr = self.exchange.nice_precision(self.exchange.clearing_rate)
		nice_bb = self.exchange.nice_precision(self.exchange.best_bid)
		nice_ba = self.exchange.nice_precision(self.exchange.best_ask)

		text_str = f'p*={nice_cp},\nu*={nice_cr},\nu_best_bid={nice_bb},\nu_best_ask={nice_ba}\n'
		plt.text(.9 * self.exchange.max_price, self.exchange.clearing_rate, text_str)

		plt.xlabel(f'(Price {self.exchange.book.base_currency}/{self.exchange.book.desired_currency})')
		plt.ylabel(f'(Quantity Traded (shares/batch)')

		plt.show(block=False)

	def pause(self, figure_num):
		plt.pause(1)

	def display(self):
		plt.show()

	def graph_as_html(self):
		fig, ax = plt.subplots()
		return mpld3.fig_to_html(fig)

	def redraw(self, figure_num):
		plt.figure(figure_num).clear()

	def close(self, figure_num):
		plt.close(figure_num)






