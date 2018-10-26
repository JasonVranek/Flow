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

		# graph the horizontal u line
		cu_array = []
		for x in range(0, int(cp)):
			cu_array.append(cu)

		# graph the vertical p line
		cp_array = []
		for x in range(0, int(cu)):
			cp_array.append(cp)

		pyplot.plot(range(0, int(cp)), cu_array, 'g-')

		pyplot.plot(cp_array, range(0, int(cu)), 'g-')
		

		# graph the vertical price line
		

		pyplot.title(f'avg of aggregates, p*={cp}, u*={cu}')
		pyplot.xlabel(f'(Price {self.exchange.book.base_currency}/{self.exchange.book.desired_currency})')
		pyplot.ylabel(f'(Quantity Traded (shares/batch)')

		
		self.fig.show()