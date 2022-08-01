from __future__ import print_function
from potentiostat import Potentiostat
import time
import sched
import math
import scipy
import matplotlib.pyplot as plt


def run_manual_test(pstat, volt, dt, t_stop, liscurr): #list of choosen currents
    """
    Run a voltammetric test in maunal/direct mode. 

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
	
        
        while t < t_stop:
            #Get current readings
            curr = pstat.get_curr()

            #Keep voltage constant unless it changes
            if curr == liscurr[i]:
                volt = volt

            #Decrease voltage
            elif curr > liscurr[i]:
                if abs(curr-liscurr[i])<3:
                	volt = volt-0.00001
                elif abs(curr-liscurr[i])<6:
                	volt = volt-0.0001
                elif abs(curr-liscurr[i])<12:
                	volt = volt-0.05
                elif abs(curr-liscurr[i])>24:
                	volt = volt-0.1
                else:
                	volt = volt-0.2
                	
            #Increase voltage
            elif curr < liscurr[i]:
                if abs(curr-liscurr[i])<3:
                	volt = volt+0.00001
                elif abs(curr-liscurr[i])<6:
                	volt = volt+0.0001
                elif abs(curr-liscurr[i])<12:
                	volt = volt+0.05
                elif abs(curr-liscurr[i])<24:
                	volt = volt+0.1
                else:
                	volt = volt+0.2
        
            #format the results
            print('{0:1.6f}, {1:1.6f}, {2:1.6f}'.format(t+(i*t_stop), volt, curr))
            time_list.append(t+(i*(t_stop)))
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

if __name__ == '__main__':

    # Run parameters
    dt = .001                          # Scan rate
    t_total = 10.0                        # Each Trial duration in sec

    liscurr = [10]      # Chosen Currents

    # Create device object, set voltage/current ranges and run test
    pstat = Potentiostat('/COM3')
    pstat.set_all_elect_connected(True)
    pstat.set_volt_range('5V')
    pstat.set_curr_range('1000uA')
    pstat.set_volt(pstat.get_volt())
    #voltage = pstat.get_volt()
    voltage = 0

    # Initials readings before adjustment
    print("Initial Readings")
    print("Initial Current", pstat.get_curr())
    print("Initial Voltage", pstat.get_volt())
    
    #The main function
    t, volt, curr = run_manual_test(pstat, voltage, dt, t_total,liscurr)
    pstat.set_all_elect_connected(False)    

    # Plot results
    plt.figure("Chronopotentiometry")
    plt.subplot(211)
    plt.plot(t,volt)
    current= ("current: "+str(liscurr)+"uA")
    plt.suptitle(t="Chronopotentiometry")
    plt.title(label=current,fontsize=10,color="black")
    plt.xlabel('time (s)')
    plt.ylabel('potential (V)')
    plt.grid('on')

    plt.show()
