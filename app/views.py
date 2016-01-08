from app import app
from flask import render_template, request, jsonify
from thermodynamics import Cycle
from rankine import compute_cycle

def cycle_to_json(cycle):
    data = {
        'states': {}
    }
    mdot = cycle.mdot
    for st in cycle.get_states():
        data['states'].update(
            {st.name : {
                'p' = st.p/1000,
                'T' = st.T-273,
                'h' = st.h/1000 * mdot,
                's' = st.s/1000 * mdot,
                'ef' = st.ef/1000 * mdot,
                'x' = st.x}
             }
        )
    return data

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/',methods=['POST','GET'])
def calc_rankine():
    if request.method == 'POST':
        valid_form = True
        if valid_form:
            props = []
            props['fluid'] = request.form['workingFluid']
            props['p_hi'] = request.form['highPressure']
            props['p_lo'] = request.form['lowPressure']
            props['t_hi'] = request.form['maxTemperature']
            props['turb_eff'] = request.form['turbineEfficiency']
            props['pump_eff'] = request.form['pumpEfficiency']
            props['mdot'] = request.form['massFlowRate']
            props['superheat'] = True
            cycle = compute_cycle(props)


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


