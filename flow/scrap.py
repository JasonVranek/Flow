import numpy as np
import matplotlib.pyplot as plt
import pickle
from util.pickle_helpers import read_file
from exchange import Exchange

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
num = 13
d = read_file(f'data/cross_fail_{num}')
c_p, c_r, bb, ba  = ex.calc_crossing(d['min_p'], d['max_p'], d['tick_size'], d['bids'], d['asks'], debug=False)
print(c_p, c_r, bb, ba)