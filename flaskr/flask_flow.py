import sys
sys.path.append('../flow/')
sys.path.append('../flow/util/')
sys.path.append('../flow/data/')

from simulation import Simulation, single_random_graph, run_simulation

from flask import Flask, render_template, Markup, session
import time

app = Flask(__name__)
app.secret_key = 'asdfasfasfdasdf'

sim = Simulation('DEX', '0xADDR', 1000, 'ETH', 'DAI')

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

@app.route("/simulation")
def run_sim():
    # sim = Simulation('DEX', '0xADDR', 1000, 'ETH', 'DAI')
    # sim.display_graph = True
    # sim.start()
    print(sim.get_html())
    session['html'] = sim.get_html()
    print('\n\n\n\nASIFDNSDFKASNFDLAAL0100012930239120931209312093190',session['html'])
    return render_template('simulation.html')

@app.route('/update_graph', methods=['GET'])
def update():
    print(str(session['html']))
    return str(session['html'])
    # return 'asdfasdf'

if __name__ == '__main__':
    app.run(debug=True)
    # sim = Simulation('DEX', '0xADDR', 1000, 'ETH', 'DAI')
    sim.display_graph = True
    sim.start()
