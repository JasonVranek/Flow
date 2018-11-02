import sys
sys.path.append('../flow/')

# from trader import Trader
# from order_book import OrderBook
# from exchange import Exchange
# from graph import Graph
from simulation import random_html_graph

from flask import Flask, Markup
import time

app = Flask(__name__)

@app.route("/")
def hello():
	html = random_html_graph(1000)
	safer = value = Markup('<strong>' + html + '</strong>')
	return safer
        #return 'hello world'

@app.route("/<num_orders>")
def rand_graph(num_orders):
	html = random_html_graph(int(num_orders))
	safer = value = Markup('<strong>' + html + '</strong>')
	return safer

@app.route("/<num_orders>")
def rand_graph(num_orders):
	html = random_html_graph(num_orders)
	safer = value = Markup('<strong>' + html + '</strong>')
	return safer


if __name__ == '__main__':
	app.run(debug=True)
