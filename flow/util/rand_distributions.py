import numpy as np
import math

class RandDists():

	def num_arrivals(batch_time, beta=.002):
		#tau is the batch length
		tau = batch_time * 1000

		# lambda is the intensity param
		lam = beta * tau

		n = np.random.poisson(int(lam))

		return n

	def rand_prices(base_p):
		# print(base_p)
		prices = np.random.poisson(float(base_p), 2)
		if prices[0] == prices[1]:
			extra = np.random.uniform(0.1, .01 * float(base_p), 1)
			print(f'adding extra: {extra[0]}')
			return prices[0], prices[1] + extra[0]
		return min(prices), max(prices)

	def rand_q_max(base_q):
		return np.random.poisson(base_q)

	def rand_u_max(base_u):
		return np.random.poisson(base_u) 

	def rand_trader_type():
		# Uniformly select either bid or ask
		choices = ['bid', 'ask']
		return choices[round(np.random.uniform(0, 1))]

	def trader_balance(base_balance):
		return np.random.poisson(base_balance)



if __name__ == '__main__':
	# print(RandDists.num_arrivals(3, beta=.002))
	# print(rand_q_max(100))
	# print(rand_u_max(100))
	for x in range(0, 100):
		print(RandDists.rand_prices(100))
	# print(RandDists.rand_trader_type())
