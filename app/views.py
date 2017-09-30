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
    props = {
        "fluid": request.args.get('workingFluid', 'Water', type=str),
        "p_hi": request.args.get('highPressure', 0.0, type=float),
        "p_lo": request.args.get('lowPressure', 0.0, type=float),
        "t_hi": request.args.get('maxTemperature', None, type=float),
        "turb_eff": request.args.get('turbineEfficiency', 1.0, type=float),
        "pump_eff": request.args.get('pumpEfficiency', 1.0, type=float),
        "cycle_mdot": request.args.get('massFlowRate', 1.0, type=float),
        "superheat":  request.args.get('superheat', False, type=bool),
    }
    cycle = compute_cycle(props)
    print cycle.serialize()
    # convert relevant data in cycle object to dict
    return jsonify(cycle=cycle.serialize())


