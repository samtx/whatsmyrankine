# Model the Rankine Cycle with Geothermal Brine Heat Source

from __future__ import print_function
import thermodynamics as thermo  # custom thermo state class in thermodynamics.py
import sys
import CoolProp.CoolProp as CP
from numbers import Number

######################################

def main():

    # The list of pure and pseudo-pure fluids that CoolProp supports can
    # be found here:
    # http://www.coolprop.org/fluid_properties/PurePseudoPure.html#list-of-fluids


    fluid_list = ['n-Butane']
    for fluid in fluid_list:
        #create dictionary of properties
        props = {}
        props["fluid"] = fluid
        props["p_hi"] = 3.5  #MPa
        props["p_lo"] = 0.3 #MPa
        props["t_hi"] =  148# deg C
        #props["t_lo"] = 10 # deg C
        props["turb_eff"] = 0.8
        props["pump_eff"] = 0.75
        props['cool_eff'] = .25 #cooling efficiency
        props['superheat'] =  False # should we allow for superheating?
        props['in_kW'] = False # print results in kW instead of kJ/kg?
        props['cycle_mdot'] = 3.14   # mass flow rate of rankine cycle working fluid in kg/s

        # begin computing processess for rankine cycle
        rankine = compute_cycle(props)

        # compute plant efficiencies
        plant = compute_plant(rankine,props)

        # print output to screen
        print_output_to_screen(plant,props)

    return

def compute_cycle(props):
    fluid = props.get('fluid',None)
    p_hi = props.get('p_hi',None)
    p_lo = props.get('p_lo',None)
    if p_hi: p_hi = p_hi * 10**6  #convert MPa to Pa
    if p_lo: p_lo = p_lo * 10**6  #convert MPa to Pa
    t_hi = props.get('t_hi',None)
    t_lo = props.get('t_lo',None)
    if t_hi: t_hi += 273.15  #convert deg C to K
    if t_lo: t_lo += 273.15  #convert deg C to K
    turb_eff = props.get('turb_eff',1.0)
    pump_eff = props.get('pump_eff',1.0)
    superheat = props.get('superheat',False)
    mdot = props.get('cycle_mdot',1.0)
    useSI = props.get('useSI', True)

    # set dead state
    dead = thermo.State(None,'Dead State',fluid)
    dead.T = 15+273  #K
    dead.p = 101325.0  #Pa
    dead.h = CP.PropsSI('H','T',dead.T,'P',dead.p,dead.fluid)
    dead.s = CP.PropsSI('S','T',dead.T,'P',dead.p,dead.fluid)

    # initialize cycle
    cyc = thermo.Cycle(fluid,name='Rankine',mdot=mdot,dead=dead)

    # check to see if enough pressures and temperatures were entered
    if superheat and not(
        p_hi and
        isinstance(t_hi, Number)):
        print('\nERROR\nIf you are superheating the fluid, specify both a high pressure and high temperature for the cycle')
        sys.exit()
    # check to see if one high and one low value were entered
    elif not superheat:
        if not (p_hi or isinstance(t_hi,Number)):
            print('\nERROR\nYou must enter at least one high value (temperature or pressure) for the cycle')
            sys.exit()
        elif not (p_lo or isinstance(t_lo,Number)):
            print('\nERROR\nYou must enter one low value (temperature or pressure) for the cycle.')
            sys.exit()

    # use pressures instead of temperatures when accessing CoolProp. So we
    # want to find the saturation pressures for the given temperatures and
    # fluid.
    if t_hi and (not superheat):
        p_hi = CP.PropsSI('P','T',t_hi,'Q',0,fluid)
    elif (not t_hi) and (not superheat):
        t_hi = CP.PropsSI('T','P',p_hi,'Q',0,fluid)
    if t_lo:
        p_lo = CP.PropsSI('P','T',t_lo,'Q',0,fluid)
    else:
        t_lo = CP.PropsSI('T','P',p_lo,'Q',0,fluid)

    # Define States
    # State 1, saturated vapor at high temperature
    st1 = thermo.State(cyc,'1')
    h_sat = CP.PropsSI('H','P',p_hi,'Q',1,fluid) #enthalpy at sat vapor
    st1.p = p_hi
    if superheat:
        st1.s = CP.PropsSI('S','P',p_hi,'T',t_hi,fluid)
        st1.h = CP.PropsSI('H','P',p_hi,'T',t_hi,fluid)
        st1.T = t_hi
        if st1.h > h_sat:
            st1.x = 'super'
        else:
            st1.x = CP.PropsSI('Q','P',p_hi,'T',t_hi,fluid)
    else:
        st1.x = 1
        st1.s = CP.PropsSI('S','P',p_hi,'Q',1,fluid)
        st1.h = h_sat
        st1.T = CP.PropsSI('T','P',p_hi,'Q',1,fluid)
        st1.u = CP.PropsSI('U','P',p_hi,'Q',1,fluid)
        st1.flow_exergy()

    # State 2s, two-phase at low temperature with same entropy as state 1
    st2s = thermo.State(cyc,'2s')
    st2s.T = CP.PropsSI('T','P',p_lo,'S',st1.s,fluid)
    st2s.p = p_lo
    st2s.s = st1.s
    sf = CP.PropsSI('S','P',p_lo,'Q',0,fluid)
    sg = CP.PropsSI('S','P',p_lo,'Q',1,fluid)
    st2s.x = (st2s.s - sf) / (sg - sf)
    hf = CP.PropsSI('H','P',p_lo,'Q',0,fluid)
    hg = CP.PropsSI('H','P',p_lo,'Q',1,fluid)
    st2s.h = st2s.x * (hg - hf) + hf
    st2s.flow_exergy()

    # State 2, two-phase at low pressure determined by turbine efficiency
    st2 = thermo.State(cyc,'2')
    # if turb_eff = 1, then just copy values from state 2s
    if turb_eff == 1:
        st2.h = st2s.h
        st2.T = st2s.T
        st2.s = st2s.s
        st2.x = st2s.x
    else:
        st2.h = turb_eff * (st2s.h - st1.h) + st1.h  #with an irreversible turbine
        st2.x = (st2.h - hf) / (hg - hf)
        st2.s = st2.x * (sg - sf) + sf
        st2.T = CP.PropsSI('T','P',p_lo,'S',st2.s,fluid)
    st2.p = p_lo
    st2.flow_exergy()

#     #print('state 2 quality: ',st2.x)
#     if st2.x > 1 and (not superheat):
#         print('Fluid is superheated after leaving turbine. Please enter a higher turbine efficiency \nExiting...')
#         sys.exit()

    # State 2b, saturated vapor at low pressure
    # --- if necessary: state 2 is superheated and we need the sat vapor state for graphing purposes
    h2b = CP.PropsSI('H','P',p_lo,'Q',1.0,fluid)  #sat vapor enthalpy
    if st2.h > h2b:
        # then state 2 is superheated. Find state 2b
        st2b = thermo.State(cyc,'2b')
        st2b.T = t_lo
        st2b.p = p_lo
        st2b.x = 1.0
        st2b.s = CP.PropsSI('S','T',t_lo,'Q',st2b.x,fluid)
        st2b.h = h2b
        st2b.flow_exergy()

    # State 3, saturated liquid at low pressure
    st3 = thermo.State(cyc,'3')
    st3.T = t_lo
    st3.p = p_lo
    st3.x = 0
    st3.s = CP.PropsSI('S','P',p_lo,'Q',st3.x,fluid)
    st3.h = CP.PropsSI('H','P',p_lo,'Q',st3.x,fluid)
    st3.v = CP.PropsSI('V','P',p_lo,'Q',st3.x,fluid)
    st3.flow_exergy()

    # States 4 and 4s, subcooled liquid at high pressure
    # assuming incompressible isentropic pump operation, let W/m = v*dp with v4 = v3
    # find values for irreversible pump operation
    wps = -st3.v * (st1.p - st3.p)
    wp = 1/pump_eff * wps
    st4s = thermo.State(cyc,'4s')
    st4s.h = st3.h - wps
    st4s.s = st3.s
    st4s.p = p_hi
    st4s.T = CP.PropsSI('T','P',p_hi,'S',st4s.s,fluid)
    st4s.x = 'sub'
    st4s.flow_exergy()
    # State 4
    st4 = thermo.State(cyc,'4')
    # if pump_eff = 1, then just copy values from state 4s
    if pump_eff == 1:
        st4.h = st4s.h
        st4.T = st4s.T
        st4.s = st4s.s
    else:
        st4.h = st3.h - wp
        #   it appears that CoolProp is pulling properties for Temperature and entropy
        #   for state 4 that are slightly lower than state 4s. These values should
        #   be higher than those at state 4s.
        #   Add logic to add a 0.1% increase in both values if they are lower.
        st4.T = CP.PropsSI('T','H',st4.h,'P',p_hi,fluid)
        if st4.T < st4s.T:
            st4.T = st4s.T * 1.001  # add 0.1% increase
        st4.s = CP.PropsSI('S','P',p_hi,'H',st4.h,fluid)
        if st4.s < st4s.s:
            st4.s = st4s.s * 1.001  # add 0.1% increase
    st4.p = p_hi
    st4.x = 'sub'
    st4.flow_exergy()
    # find State 4b, high pressure saturated liquid
    st4b = thermo.State(cyc,'4b')
    st4b.p = p_hi
    st4b.T = t_hi
    st4b.x = 0.0
    st4b.h = CP.PropsSI('H','P',p_hi,'Q',st4b.x,fluid)
    st4b.s = CP.PropsSI('S','T',t_hi,'Q',st4b.x,fluid)
    st4b.flow_exergy()

    # State 4c for graphing purposes. Sat vapor at p_hi
    if st1.x == 'super':
        st4c = thermo.State(cyc,'4c')
        st4c.T = CP.PropsSI('T','P',p_hi,'Q',1,fluid)
        st4c.s = CP.PropsSI('S','P',p_hi,'Q',1,fluid)
        st4c.h = CP.PropsSI('H','P',p_hi,'Q',1,fluid)
        st4c.p = p_hi
        st4c.x = 1

    # Define processes
    # Find work and heat for each process
    turb = thermo.Process(cyc,st1, st2, 0, st1.h-st2.h, "Turbine")
    cond = thermo.Process(cyc,st2, st3, st3.h-st2.h, 0, "Condenser")
    pump = thermo.Process(cyc,st3, st4, 0, wp, "Pump")
    boil = thermo.Process(cyc,st4, st1, st1.h-st4.h, 0, "Boiler")

    # calculate exergy values for each process
    # Boiler
    boil.ex_in = boil.delta_ef
    boil.ex_d = 0
    boil.ex_out = 0
    boil.ex_eff = 1
    boil.ex_bal = boil.ex_in - boil.ex_out - boil.delta_ef - boil.ex_d
    # add results to cycle exergy totals
    cyc.ex_in += boil.ex_in
    cyc.ex_d += boil.ex_d
    cyc.ex_out += boil.ex_out
    cyc.delta_ef += boil.delta_ef

    # Turbine
    turb.ex_in = 0
    turb.ex_d = turb.cycle.dead.T * (turb.out.s - turb.in_.s)
    turb.ex_out = turb.work
    turb.ex_eff = turb.ex_out / -turb.delta_ef
    turb.ex_bal = turb.ex_in - turb.ex_out - turb.delta_ef - turb.ex_d
    # add results to cycle exergy totals
    cyc.ex_in += turb.ex_in
    cyc.ex_d += turb.ex_d
    cyc.ex_out += turb.ex_out
    cyc.delta_ef += turb.delta_ef

    # Condenser
    cond.ex_in = 0
    cond.ex_d = 0
    cond.ex_out = -cond.delta_ef
    cond.ex_eff = 1
    cond.ex_bal = cond.ex_in - cond.ex_out - cond.delta_ef - cond.ex_d
    # add results to cycle exergy totals
    cyc.ex_in += cond.ex_in
    cyc.ex_d += cond.ex_d
    cyc.ex_out += cond.ex_out
    cyc.delta_ef += cond.delta_ef

    # Pump
    pump.ex_out = 0
    pump.ex_in = -pump.work
    pump.ex_d = pump.cycle.dead.T * (pump.out.s - pump.in_.s)
    pump.ex_eff = pump.delta_ef / pump.ex_in
    pump.ex_bal = pump.ex_in - pump.ex_out - pump.delta_ef - pump.ex_d
    # add results to cycle exergy totals
    cyc.ex_in += pump.ex_in
    cyc.ex_d += pump.ex_d
    cyc.ex_out += pump.ex_out
    cyc.delta_ef += pump.delta_ef

    # Define cycle properties
    cyc.wnet = turb.work + pump.work
    cyc.qnet = boil.heat + cond.heat
    cyc.en_eff = cyc.wnet / boil.heat
    cyc.bwr = -pump.work / turb.work
    cyc.ex_eff = cyc.wnet / boil.delta_ef  # cycle exergetic eff

    return cyc

def compute_plant(rank,props):
    ''' Compute and return plantplo object from rankine cycle and geothermal cycle objects '''
    cool_eff = props.get('cool_eff',1.0) # cooling efficiency
    # initialize geothermal cycle using defaults defined in object
    fluid = 'Salt Water, 20% salinity'
    # set brine dead state
    dead = thermo.State(None,'Br.Dead',fluid)
    dead.h = 61.05 * 1000 # J/kg
    dead.s = 0.2205 * 1000 # J/kg.K
    dead.T = 15 + 273 # K
    dead.p = 101325 # Pa
    geo = thermo.Geotherm(fluid=fluid,dead=dead)

    #   Find the mass flow rate of the brine based on cooling efficiency and
    #   the heat gained by the boiler in the Rankine cycle.
    # first, get the heat from the boiler process
    heat = 0.0
    for p in rank.get_procs():
        if 'boil' in p.name.lower():
            heat = p.heat
    # create initial brine state
    g1 = thermo.State(geo,'Br.In')
    g1.s = 1.492 * 1000 # J/kg.K
    g1.h = 491.6 * 1000 # J/kg
    g1.T = 120 + 273.15 # K
    g1.p = 5 * 10**5    # bars to Pa
    g1.flow_exergy()
    geo.in_ = g1
    # set brine mass flow rate
    geo.mdot = (rank.mdot * heat) / (cool_eff * (geo.in_.h - geo.dead.h))

    # initialize plant object using rankine and geothermal cycles
    plant = thermo.Plant(rank,geo)
    # set cooling efficiency
    plant.cool_eff = cool_eff
    #   Calculate plant energetic efficiency
    q_avail = geo.mdot * (geo.in_.h - geo.dead.h)
    plant.en_eff = (rank.mdot * rank.wnet) / q_avail
    # calculate plant exergetic efficiency
    plant.ex_eff = (rank.mdot * rank.wnet) / (geo.mdot * geo.in_.ef)

    return plant

##############################################################################
# ------------------- Print output functions ---------------------------------
##############################################################################

def print_output_to_screen(plant,props):
    in_kW = props.get('in_kW',False)
    print_user_values(props)
    print('Rankine Cycle States and Processes    (Working Fluid: '+plant.rank.fluid+')')
    print_state_table(plant.rank,in_kW)
    print_process_table(plant.rank,in_kW)
    print_exergy_table(plant.rank,in_kW)
    create_plot(plant.rank, props)
    print('\nGeothermal Cycle States and Processes    (Brine: '+plant.geo.fluid+')')
    print_state_table(plant.geo,in_kW)
    if plant.geo.get_procs():
        # only print process table for brine if processes have been defined.
        print_process_table(plant.geo.in_kW)
        print_exergy_table(plant.geo,in_kW)
    print_plant_results(plant)
    return

def print_user_values(props):
    # print values to screen
    fluid = props.get('fluid',None)
    p_hi = props.get('p_hi',None)
    p_lo = props.get('p_lo',None)
    t_hi = props.get('t_hi',None)
    t_lo = props.get('t_lo',None)
    turb_eff = props.get('turb_eff',1.0)
    pump_eff = props.get('pump_eff',1.0)
    print('\nUser entered values\n-------------------')
    print('Working Fluid: '+fluid)
    if t_lo: print('Low Temperature:  {:>3.1f} deg C'.format(t_lo))
    if t_hi: print('High Temperature: {:>3.1f} deg C'.format(t_hi))
    if p_lo: print('Low Pressure:  {:>5.4f} MPa'.format(p_lo))
    if p_hi: print('High Pressure: {:>5.4f} MPa'.format(p_hi))
    print('Isentropic Turbine Efficiency: {:>2.1f}%'.format(props["turb_eff"]*100))
    print('Isentropic Pump Efficiency:    {:>2.1f}%'.format(props["pump_eff"]*100))
    print('Plant Cooling Efficiency:      {:>2.1f}%\n'.format(props["cool_eff"]*100))
    return



def print_cycle_values(cycle):
    print('\nCycle Values \n------------ ')
    print('thermal efficiency = {:2.1f}%'.format(cycle.en_eff*100))
    print('back work ratio = {:.3f}'.format(cycle.bwr))
    return



def print_plant_results(plant):
    print('Plant Results \n------------------ ')
    print('Rankine Cycle mass flow rate  =   {:>3.2f} kg/s'.format(plant.rank.mdot))
    print('Geo. Brine mass flow rate     =   {:>3.2f} kg/s'.format(plant.geo.mdot))
    print('Plant thermal (energetic) eff = {:>6.1f}%'.format(plant.en_eff*100))
    print('Plant exergetic efficiency    = {:>6.1f}%'.format(plant.ex_eff*100))
    print('Plant cooling eff. (user specified) = {:>6.1f}%'.format(plant.cool_eff*100))
    print('Rankine cycle thermal eff     = {:>6.1f}%'.format(plant.rank.en_eff*100))
    print('Rankine cycle exergetic eff   = {:>6.1f}%'.format(plant.rank.ex_eff*100))
    print('Rankine cycle back work ratio =  {:>6.2f}%'.format(plant.rank.bwr*100))
    return


if __name__ == '__main__':
    main()