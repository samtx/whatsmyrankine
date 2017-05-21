from app import app
from flask import render_template, jsonify, request
from rankine import compute_cycle

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)
    
@app.route('/_runcycle')
def runcycle():
    props = {}
    props["fluid"] = request.args.get('workingFluid', 'Water', type=str)
    props["p_hi"] = request.args.get('highPressure', 0.0, type=float)
    props["p_lo"] = request.args.get('lowPressure', 0.0, type=float)
    cycle = compute_cycle(props)
    return jsonify(therm_eff=cycle.en_eff)


