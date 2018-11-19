from util.pickle_helpers import read_file
from exchange import Exchange 
import sys
sys.path.append('../')
sys.path.append('../util')
sys.path.append('../data')


num = 13
d = read_file(f'data/cross_fail_{num}')
c_p, c_r, bb, ba  = Ex.calc_crossing(d['min_p'], d['max_p'], d['tick_size'], d['bids'], d['asks'], debug=False)
print(c_p, c_r, bb, ba)

