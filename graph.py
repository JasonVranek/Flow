from matplotlib import pyplot
class Graph():

	def __init__(self):
		self.exchange = object

	def set_exchange(self, exchange):
		self.exchange = exchange

	def graph_all_aggregates(self):
		pyplot.clf()
		for ss in self.exchange.aggregate_supply:
			pyplot.plot(ss[1][:,1], ss[1][:,0], 'b')

		for dd in self.exchange.aggregate_demand:
			pyplot.plot(dd[1][:,1], dd[1][:,0], 'r')

		pyplot.show()