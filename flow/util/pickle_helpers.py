import pickle

def read_file(filename):
	file = open(filename, 'rb')
	data = pickle.load(file)
	file.close()
	return data

def get_books(batch_num):
	bids = read_file(f'../data/bids_{batch_num}')
	asks = read_file(f'../data/asks_{batch_num}')
	result = read_file(f'../data/result_{batch_num}')

	return bids, asks, result