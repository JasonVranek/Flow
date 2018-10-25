from matplotlib import pyplot
class Graph():

	def __init__(self):
		self.exchange = object
		self.fig = []

	def set_exchange(self, exchange):
		self.exchange = exchange

	def graph_all_aggregates(self):
		pyplot.figure(2)
		for ss in self.exchange.aggregate_supply:
			pyplot.plot(ss[1][:,1], ss[1][:,0], 'b')

		for dd in self.exchange.aggregate_demand:
			pyplot.plot(dd[1][:,1], dd[1][:,0], 'r')

		pyplot.show()

	def graph_supply_demand(self, supply, demand):
		self.fig = pyplot.figure(1)

		# plot supply
		pyplot.plot(supply[:,1], supply[:,0], 'b')

		# plot demand
		pyplot.plot(demand[:,1], demand[:,0], 'r')

		self.fig.show()