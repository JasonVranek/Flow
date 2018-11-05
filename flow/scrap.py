import numpy as np
import matplotlib.pyplot as plt
import pickle

'''
#tau is the batch length
tau = 3000

# beta is expected wait time for traders to arrive
beta = (1 / 300) 
beta = .003

# lambda is the intensity param
lam = beta * tau

n = np.random.poisson(int(lam))

print(n)

# uniform_n = np.random.uniform(n)

# print(n, uniform_n)
# print(f'num_items {len(n)}, num_arrivals {sum(n)}')

# count, bins, ignored = plt.hist(n, 14, density=True)
# plt.show()

'''
filename = 'data/result_1'
file = open(filename, 'rb')
bid_1 = pickle.load(file)
file.close()
print(bid_1)