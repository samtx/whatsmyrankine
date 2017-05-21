import matplotlib   # for pretty pictures
matplotlib.use('Agg') # to get matplotlib to save figures to a file instead of using X windows
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP

def create_plot(cycle, props):
    p_list = cycle.get_states()
    s_list = cycle.get_states()
    superheat = s_list[3].name
    fluid = cycle.fluid

    #Check to see if the system is superheated

    if superheat == '2b':
      st_1 = s_list[0]
      st_2s = s_list[1]
      st_2 = s_list[2]
      st_2b= s_list[3]
      st_3 = s_list[4]
      st_4s = s_list[5]
      st_4 = s_list[6]
      st_4b = s_list[7]
      T_pts = [st_1.T, st_2s.T, st_2.T, st_2b.T, st_3.T, st_4s.T, st_4b.T, st_1.T] # solid lines
      s_pts = [st_1.s, st_2s.s, st_2.s, st_2b.s, st_3.s, st_4s.s, st_4b.s, st_1.s]
    else:
      st_1 = s_list[0]
      st_2s = s_list[1]
      st_2 = s_list[2]
      st_3 = s_list[3]
      st_4s = s_list[4]
      st_4 = s_list[5]
      st_4b = s_list[6]
      T_pts = [st_1.T, st_2s.T, st_2.T, st_3.T, st_4s.T, st_4b.T, st_1.T] # solid lines
      s_pts = [st_1.s, st_2s.s, st_2.s, st_3.s, st_4s.s, st_4b.s, st_1.s]

    # unpack processes
    turb = p_list[0]
    cond = p_list[1]
    pump = p_list[2]
    boil = p_list[3]
    #get the points to plot the saturation dome

    (dspts,dtpts) = get_sat_dome(cycle)


    s_dash_12 = [st_1.s, st_2.s]
    T_dash_12 = [st_1.T, st_2.T]
    s_dash_34 = [st_3.s, st_4.s]
    T_dash_34 = [st_3.T, st_4.T]
    #s_super

    # Draw T-s plot
    plt.clf()
    plt.plot(s_pts,T_pts, 'b')
    plt.plot(s_dash_12,T_dash_12,'g--',s_dash_34,T_dash_34,'g--')
    #PropsPlot(cycle.fluid,'Ts',units="KSI")
    #plotting the vapor dome...hopefully
    plt.plot(dspts,dtpts, 'r--')
    #appropriate point labels for the plot
    if superheat == '2b':
      #points for a superheated fluid
      plt.annotate("1.", xy = (s_pts[0],T_pts[0]) , xytext = (s_pts[0] + 2,T_pts[0]+20 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("2s.", xy = (s_pts[1],T_pts[1]) , xytext = (s_pts[1] + 2,T_pts[1]+25 ), arrowprops=dict(facecolor = 'black', shrink=0.05),)
      plt.annotate("2.", xy = (s_pts[2],T_pts[2]) , xytext = (s_pts[2] + 2,T_pts[2]+25 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("3.", xy = (s_pts[4],T_pts[4]) , xytext = (s_pts[4] - 800,T_pts[4] ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("4./4s.", xy =  (s_pts[5],T_pts[5]) , xytext = (s_pts[5] + 2,T_pts[5]+30 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      #plt.annotate("2B", xy =  (s_pts[3],T_pts[3]) , xytext = (s_pts[3] + 2,T_pts[3]+30 ), arrowprops=dict(facecolor = 'red', shrink=0.05),)
    else:
    #points for no superheated fluid
      plt.annotate("1.", xy = (s_pts[0],T_pts[0]) , xytext = (s_pts[0] + 2,T_pts[0]+20 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("2s.", xy = (s_pts[1],T_pts[1]) , xytext = (s_pts[1] + 2,T_pts[1]+25 ), arrowprops=dict(facecolor = 'black', shrink=0.05),)
      plt.annotate("2.", xy = (s_pts[2],T_pts[2]) , xytext = (s_pts[2] + 2,T_pts[2]+25 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("3.", xy = (s_pts[3],T_pts[3]) , xytext = (s_pts[3] - 800,T_pts[3] ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("4./4s.", xy =  (s_pts[4],T_pts[4]) , xytext = (s_pts[4] + 2,T_pts[4]+30 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      #plt.annotate("b.", xy =  (s_pts[5],T_pts[5]) , xytext = (s_pts[5] + 2,T_pts[5]+30 ), arrowprops=dict(facecolor = 'red', shrink=0.05),)

    #plt.annotate("4b.", xy = (s_dash_34[1],T_dash_34[1]) , xytext = (s_dash_34[1] + 500, T_dash_34[1] + 2 ), arrowprops=dict(facecolor = 'black', shrink=0.05),)
    title_txt = 'Rankine Cycle T-S Diagram: ' + fluid
    #print (title_txt)
    plt.suptitle(title_txt)
    plt.xlabel("Entropy (J/kg.K)")
    plt.ylabel("Temperature (deg K)")
    # Save plot
    filename = 'ts_plot.png'
    plt.savefig(filename) # save figure to directory
    return

def get_sat_dome(cycle):
    fluid = cycle.fluid
    slist = cycle.get_states()
    # find min temp to use for dome
    t_state_min = 300  # default room temp in K
    #print('slist:',slist)
    for state in slist[:-1]:
        #print('state.T:',state.T)
        t_state_min = min([state.T,t_state_min])
    t_fluid_min = CP.PropsSI('TMIN',fluid)
    #print('t_fluid_min:',t_fluid_min)
    #print('t_state_min:',t_state_min)
    tmin = max([t_fluid_min,t_state_min-10]) # add 10 deg cushion
    tcrit = CP.PropsSI('TCRIT',fluid)  # critical temp for fluid
    #print('tcrit=',tcrit,' pcrit=',pcrit,' scrit=',scrit)
    liq_pts = []
    vap_pts = []
    tpts = []
    spts = []

    # for temps from tmin to tmax, find entropy at both sat liq and sat vap.
    t = tmin  # initial temp for dome
    dt = 1.0
    #print('tmin:',tmin)
    while t < tcrit:
        s = CP.PropsSI('S','T',t,'Q',0,fluid)
        liq_pts.append((s,t))
        s = CP.PropsSI('S','T',t,'Q',1,fluid)
        vap_pts.append((s,t))
        t += dt
    # now, unravel the liq_pts and vap_pts tuples to make the spts and tpts lists
    for item in liq_pts:
        spts.append(item[0])
        tpts.append(item[1])
    for item in vap_pts[::-1]:
        spts.append(item[0])
        tpts.append(item[1])
    return spts, tpts