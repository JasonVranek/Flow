import sys
sys.path.append('../flow/')

from simulation import single_random_graph

from flask import Flask, Markup
import time

app = Flask(__name__)

@app.route("/")
def hello():
	html = single_random_graph(1000)
	safer = value = Markup('<strong>' + html + '</strong>')
	return safer
        #return 'hello world'

@app.route("/<int:num_orders>")
def rand_graph(num_orders):
	html = single_random_graph(num_orders)
	safer = value = Markup('<strong>' + html + '</strong>')
	return safer

if __name__ == '__main__':
	app.run(debug=True)
