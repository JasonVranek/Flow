import numpy as np
import matplotlib.pyplot as plt
import pickle
from util.pickle_helpers import read_file
from exchange import Exchange
from graph import Graph

#tau is the batch length
# tau = 3000

# # beta is expected wait time for traders to arrive
# beta = (1 / 300) 
# beta = .003

# # lambda is the intensity param
# lam = beta * tau

# n = np.random.poisson(int(lam))

# print(n)

# uniform_n = np.random.uniform(n)

# print(n, uniform_n)
# print(f'num_items {len(n)}, num_arrivals {sum(n)}')

# count, bins, ignored = plt.hist(n, 14, density=True)
# plt.show()

ex = Exchange('name', 'asddr')

for num in range(0, 20):
	try:
		d = read_file(f'data/cross_fail_{num}')
		results  = ex.calc_crossing(d['min_p'], d['max_p'], d['tick_size'], d['bids'], d['asks'], debug=False)
		c_p, c_r, bb, ba = results
		print(c_p, c_r, bb, ba)

		# Graph.test_graph(d['min_p'], d['max_p'], d['tick_size'], d['bids'], d['asks'], c_p, c_r)
		Graph.test_graph(d['min_p'], d['max_p'], d['tick_size'], d['bids'], d['asks'], c_p, c_r)
	except Exception as e:
		pass