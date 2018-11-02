import sys
sys.path.append('../flow/')

from trader import Trader
from order_book import OrderBook
from exchange import Exchange
from graph import Graph
from simulation import random_html_graph

from flask import Flask
import random
import numpy as np
import time

from profiler import prof

app = Flask(__name__)

@app.route("/")
def hello():
	html = random_html_graph(50)
	return html


if __name__ == '__main__':
	app.run(debug=True)