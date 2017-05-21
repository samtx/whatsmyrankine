from prettytable import PrettyTable, MSWORD_FRIENDLY, PLAIN_COLUMNS #for output formatting

def print_state_table(cycle,in_kW=False):
    s_list = cycle.get_states()
    s_list.append(cycle.dead)
    if in_kW:
        headers = ['State','P(kPa)','T(deg C)','H(kW)','S(kW/K)','Ef(kW)','x']
    else:
        headers = ['State','P(kPa)','T(deg C)','h(kJ/kg)','s(kJ/kg.K)','ef(kJ/kg)','x']
    t = PrettyTable(headers)
    for item in headers[1:6]:
        t.align[item] = 'r'
    for item in headers[2:4]:
        t.float_format[item] = '4.2'
    t.float_format[headers[1]] = '5.0'
    t.float_format[headers[4]] = '6.5'
    t.float_format[headers[5]] = '4.2'
    t.float_format[headers[6]] = '0.2'
    t.padding_width = 1
    if in_kW:
        mdot = cycle.mdot
    else:
        mdot = 1.0
    for item in s_list:
        #print('item.name = ',item.name)
        t.add_row([item.name[:6],
                   item.p/1000,
                   item.T-273,
                   item.h/1000 * mdot,
                   item.s/1000 * mdot,
                   item.ef/1000 * mdot,
                   item.x])
    print(t)
    return

def print_process_table(cycle,in_kW=False):
    p_list = cycle.get_procs()
    if in_kW:
        headers = ['Proc','State','Q(kW)','W(kW)']
    else:
        headers = ['Proc','State','Q(kJ/kg)','W(kJ/kg)']
    t = PrettyTable(headers)
    #t.set_style(MSWORD_FRIENDLY)
    for item in headers[2:]:
        t.align[item] = 'r'
        t.float_format[item] = '5.1'
    if in_kW:
        mdot = cycle.mdot
    else:
        mdot = 1.0
    for p in p_list:
        t.add_row([p.name[:4],p.in_.name[:5]+' -> '+p.out.name[:5],
                   p.heat/1000 * mdot,
                   p.work/1000 * mdot])
    # add totals row
    t.add_row(['Net','',
               cycle.qnet/1000 * mdot,
               cycle.wnet/1000 * mdot])
    print(t)
    return

def print_exergy_table(cycle,in_kW):
    p_list = cycle.get_procs()
    if in_kW:
        headers = ['Proc','State','Ex.In(kW)','Ex.Out(kW)','Delt.Ef(kW)','Ex.D(kW)','Ex.Eff.','Ex.Bal']
    else:
        headers = ['Proc','State','Ex.In(kJ/kg)','Ex.Out(kJ/kg)','delt.ef(kJ/kg)','Ex.D(kJ/kg)','Ex.Eff.','Ex.Bal']
    t = PrettyTable(headers)
    #t.set_style(MSWORD_FRIENDLY)
    for item in headers[2:]:
        t.align[item] = 'r'
        t.float_format[item] = '5.1'
    if in_kW:
        mdot = cycle.mdot
    else:
        mdot = 1.0
    for p in p_list:
        t.add_row([p.name[:4],p.in_.name[:5]+'->'+p.out.name[:5],
                   p.ex_in/1000 * mdot,
                   p.ex_out/1000 * mdot,
                   p.delta_ef/1000 * mdot,
                   p.ex_d/1000 * mdot,
                   '{:.1%}'.format(p.ex_eff),
                   p.ex_bal/1000 * mdot])
    # add totals row
    t.add_row(['Net','',
               cycle.ex_in/1000 * mdot,
               cycle.ex_out/1000 * mdot,
               cycle.delta_ef/1000 * mdot,
               cycle.ex_d/1000 * mdot,
               '{:.1%}'.format(cycle.ex_eff),
               'n/a'])
    print(t)
    return