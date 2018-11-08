import sys
sys.path.append('../flow/')
sys.path.append('../flow/util/')
sys.path.append('../flow/data/')

from simulation import Simulation, single_random_graph, run_simulation

from flask import Flask, render_template, Markup, session
import time

from threading import Thread

app = Flask(__name__)
app.secret_key = 'asdfasfasfdasdf'

@app.route("/")
def hello():
    html = single_random_graph(1000)
    safer = Markup('<strong>' + html + '</strong>')
    return safer
    #return 'hello world'

@app.route("/<int:num_orders>")
def rand_graph(num_orders):
    html = single_random_graph(num_orders)
    safer = Markup('<strong>' + html + '</strong>')
    return safer

# @app.route("/simulation")
# def run_sim():
#     return render_template('simulation.html')

@app.route("/simulation")
def test():
    # run_simulation(False)
    t = Thread(target=simulate)
    t.daemon = True
    t.start()
    return render_template('simulation.html')

def simulate():
    try:
        run_simulation(False)
    except Exception as e:
        print('oops ', e)

@app.route('/update_graph', methods=['GET'])
def get_html():
    with open('../html/market.html') as file:
        html = file.read()

    # print(html)
    return html

if __name__ == '__main__':
    app.run(debug=True)
