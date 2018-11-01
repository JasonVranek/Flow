from matplotlib import pyplot
import numpy as np

class Graph():

	def __init__(self):
		self.exchange = object

	def set_exchange(self, exchange):
		self.exchange = exchange

	def graph_all_aggregates(self, figure_num, c_d, c_s):
		pyplot.figure(figure_num)
		price_range = []

		try:
			for x in range(0, len(self.exchange.aggregate_supply[:,0])):
				price_range.append(x * self.exchange._min_tick_size)
			for schedule in self.exchange.aggregate_supply.T:
				pyplot.plot(price_range, schedule, c_s)
		except IndexError:
			pass

		price_range = []
		try:
			for x in range(0, len(self.exchange.aggregate_demand[:,0])):
				price_range.append(x * self.exchange._min_tick_size)
			for schedule in self.exchange.aggregate_demand.T:
				pyplot.plot(price_range, schedule, c_d)
		except IndexError:
			pass

		pyplot.title('order books supply and demands')
		text_str = f'num_bids: {self.exchange.num_active_bids}\nnum_asks: {self.exchange.num_active_asks}\n'
		pyplot.text(0.05, 0.5, text_str)

		pyplot.show(block=False)

	def graph_total_aggregates(self, figure_num, c_d, c_s, c_c):
		pyplot.figure(figure_num)

		price_range = []
		try:
			for x in range(0, len(self.exchange.total_aggregate_supply)):
				price_range.append(x * self.exchange._min_tick_size)
		except IndexError:
			pass

		pyplot.plot(price_range, self.exchange.total_aggregate_supply, c_s)

		pyplot.plot(price_range, self.exchange.total_aggregate_demand, c_d)

		cp = self.exchange.clearing_price
		cu = self.exchange.clearing_rate

		# graph the horizontal rate line
		cu_array = []
		for x in range(0, int(cp)):
			cu_array.append(cu)
		pyplot.plot(range(0, int(cp)), cu_array, c_c)

		# graph the vertical price line
		cp_array = []
		for x in range(0, int(cu)):
			cp_array.append(cp)
		pyplot.plot(cp_array, range(0, int(cu)), c_c)
		
		pyplot.title(f'total of aggregates')#, p*={cp}, u*={cu} \n \
			#best_bid={self.exchange.best_bid}, best_ask={self.exchange.best_ask}')
		
		text_str = f'p*={cp},\nu*={cu},\nu_best_bid={self.exchange.best_bid},\nu_best_ask={self.exchange.best_ask}\n'
		pyplot.text(0.05, 0.5, text_str)

		pyplot.xlabel(f'(Price {self.exchange.book.base_currency}/{self.exchange.book.desired_currency})')
		pyplot.ylabel(f'(Quantity Traded (shares/batch)')

		pyplot.show(block=False)

	def display(self):
		pyplot.show()

	def redraw(self, figure_num):
		pyplot.figure(figure_num).clear()






