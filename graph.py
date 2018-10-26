from matplotlib import pyplot
import numpy as np

class Graph():

	def __init__(self):
		self.exchange = object
		self.fig = []

	def set_exchange(self, exchange):
		self.exchange = exchange

	def graph_all_aggregates(self):
		pyplot.figure(2)
		price_range = []
		for x in range(0, len(self.exchange.aggregate_supply[:,0])):
			price_range.append(x * self.exchange._min_tick_size)

		for schedule in self.exchange.aggregate_supply.T:
			pyplot.plot(price_range, schedule, 'b')

		for schedule in self.exchange.aggregate_demand.T:
			pyplot.plot(price_range, schedule, 'r')

		pyplot.title('order books supply and demands')
		pyplot.show()

	def graph_average_aggregates(self):
		self.fig = pyplot.figure(1)

		price_range = []
		for x in range(0, len(self.exchange.avg_aggregate_supply)):
			price_range.append(x * self.exchange._min_tick_size)

		pyplot.plot(price_range, self.exchange.avg_aggregate_supply, 'b')

		pyplot.plot(price_range, self.exchange.avg_aggregate_demand, 'r')

		cp = self.exchange.clearing_price
		cu = self.exchange.clearing_rate

		# # graph the horizontal u line
		# x_0 = self.exchange.avg_aggregate_demand[0, 1]
		# price_x_array = np.arange(x_0, cp, 1)
		# price_y_array = []
		# for x in range(0, len(price_x_array)):
		# 	price_y_array.append(cu)
		# pyplot.plot(price_x_array, price_y_array, 'g.')

		# # graph the vertical price line
		# y_coords = np.arange(0, cu, cu / 15)
		# x_coords = []
		# for x in range(0, len(y_coords)):
		# 	x_coords.append(cp)
		# pyplot.plot(x_coords, y_coords, 'g.')

		pyplot.title(f'avg of aggregates, p*={cp}, u*={cu}')
		pyplot.xlabel(f'(Price {self.exchange.book.base_currency}/{self.exchange.book.desired_currency})')
		pyplot.ylabel(f'(Quantity Traded (shares/batch)')

		
		self.fig.show()