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
                'name' = st.name,
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
            props['fluid'] = request.data['workingFluid']
            props['p_hi'] = request.data['highPressure']
            props['p_lo'] = request.data['lowPressure']
            props['t_hi'] = request.data['maxTemperature']
            props['turb_eff'] = request.data['turbineEfficiency']
            props['pump_eff'] = request.data['pumpEfficiency']
            props['mdot'] = request.data['massFlowRate']
            props['superheat'] = True
            cycle = compute_cycle(props)
            data = cycle_to_json(cycle)
            return jsonify(data)


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


