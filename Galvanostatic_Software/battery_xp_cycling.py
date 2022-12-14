from __future__ import print_function
from potentiostat import Potentiostat
import time
import sched
import math
import scipy
import matplotlib.pyplot as plt


def run_manual_test(pstat, volt, dt, t_stop, liscurr): #list of choosen currents
    """
    Run a galvanostatic test in manual/direct mode through the
    implementation of a feedback loop. Voltage will adjust to desired current. 

    pstat      = potentiostat
    volt_func  = output voltage function
    dt         = sample time step
    t_stop     = time for each trial
    """
    time_list, volt_list, curr_list = [], [], []

    print('{0:1.4s}, {1:1.4s}, {2:1.4s}'.format("Time", "Voltage", "Current"))
    
    for i in range(len(liscurr)):
        t = 0
        cnt = 0
        t_prev = 0
        t_start = time.time()
        scheduler = sched.scheduler(time.time, time.sleep)
	
    
        while lisvolt[i] != round(volt,3):
   
            #Get current readings
            curr = pstat.get_curr()
            
            #adjust voltage to desired current
            volt = volt_adjustment(curr, liscurr, i, volt)
        
            #format the results
            #print('{0:1.6f}, {1:1.6f}, {2:1.6f}'.format(t+(i*t_stop), volt, curr))
            print('{0:1.6f}, {1:1.6f}, {2:1.6f}'.format(t,volt,curr))
            #time_list.append(t+(i*(t_stop)))
            time_list.append(t)
            volt_list.append(volt)
            curr_list.append(curr)

            # Run scheduler to until time for the next sample (dt seconds)
            t_next = t_start + (cnt+1)*dt
            scheduler.enterabs(t_next, 1, lambda:None, ())
            scheduler.run()
            t = time.time() - t_start
            cnt+=1

            #Setting voltage w/response from current
            pstat.set_volt(volt)

    return time_list, volt_list, curr_list

def volt_adjustment(curr, liscurr, i, volt):
    """
    feedback loop to adjust voltage accordingly to get
    desired current
    returns: voltage
    """
    #Keep voltage constant unless it changes
    if curr == liscurr[i]:
        volt = volt

    #Decrease voltage
    elif curr > liscurr[i]:
        if abs(curr-liscurr[i])<3:
            volt = volt-0.00001
        elif abs(curr-liscurr[i])<20:
            volt = volt-0.0001
        else:
            volt = volt-0.001
                	
    #Increase voltage
    elif curr < liscurr[i]:
        if abs(curr-liscurr[i])<3:
            volt = volt+0.00001
        elif abs(curr-liscurr[i])<20:
            volt = volt+0.0001
        else:
            volt = volt+0.001
    return volt


if __name__ == '__main__':

    # Run parameters
    dt = .001                # Scan rate seconds    
    t_total = 360.0         # Each Trial duration in sec
    #amount of curr values must equal amount of volt values
    liscurr = [-100, 100, -100, 100]      # Chosen Applied Currents
    lisvolt = [0.005, 1.5, 0.005, 1.5]     # Chosen Applied Volt 

    # Create device object, set voltage/current ranges and run test
    pstat = Potentiostat('/COM3')
    pstat.set_all_elect_connected(True)
    pstat.set_volt_range('5V')
    pstat.set_curr_range('1000uA')

    #Set starting voltage to batteries equilibrium
    print("Initial Voltage: ",pstat.get_volt())
    pstat.set_volt(pstat.get_volt()) 
    voltage = pstat.get_volt()
    print("Initial Current", pstat.get_curr())
  
    #The main function
    t, volt, curr = run_manual_test(pstat, voltage, dt, t_total,liscurr)
    pstat.set_all_elect_connected(False)    

    # Plot results voltage vs time
    plt.figure("Cycling")
    plt.subplot(211)
    plt.plot(t,volt)
    current= ("current: "+str(liscurr)+"uA")
    plt.suptitle(t="Cycling")
    plt.title(label=current,fontsize=10,color="black")
    plt.xlabel('time (s)')
    plt.ylabel('potential (V)')
    plt.grid('on')

    plt.show()
