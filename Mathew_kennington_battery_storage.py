## Modelling a potential energy system: hydro + domestic solar PV generation with EV balancing ##

# import relevant packages
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import datetime

# import data
solar_profile = pd.read_csv("https://bitbucket.org/scotwheeler/oxemf_3yp/raw/5d950da31a156418c8abfa1dd86668688715e98e/data/solar_example.csv", usecols=[1]).values
load_profile = pd.read_csv('https://bitbucket.org/scotwheeler/oxemf_3yp/raw/5d950da31a156418c8abfa1dd86668688715e98e/data/load_example.csv', usecols=[1]).values

# calculate annual generation
print("Annual Solar Generation: {:.2f} kWh".format(solar_profile.sum())) #3381.96 KWh

## 3381.96 KWh per year corresponds to the average yearly generation of a typical single 4 KW system installed for a UK household.
## [source: https://www.in2gr8tedsolutions.co.uk/info/solar-generation-calculator.php; this says 3500 KWh is typical.] 
## Kennington consumes 6,702 MWh of electricity and Sandford Hydro generates 1,540 MWh of electricity per year. The yearly deficit is therefore 5,162 MWh. 
## I must therefore scale our solar generation by a factor of 5,162*1000/3381.96 = 1,526.25. This corresponds to 1,527 x 4 KW PV installations.
## The number of houses (detached+semidetached+terraced) in Kennington is 1,558. The number of households in Kennington is 1,695. 
## [source: https://www.communityfirstoxon.org/wp-content/uploads/2016/07/RuralPlaceProfile_E04012130_Kennington.pdf]

# calculate annual demand
print("Annual Demand : {:.2f} kWh".format(load_profile.sum())) #4030.00 KWh

## 4030.00 KWh per year corresponds to the average yearly electricity consumption of a typical UK household.
## The number of households in Kennington is 1,695 therefore the expected electricity consumption is 6,830.85 MWh. 
## The actual electricity consumption is stated above; this data therefore overestimates consumption which is good!

# plot data together
fig,ax =  plt.subplots(nrows=3,ncols=2,sharex=True,sharey=False)
fig.tight_layout(pad=3.0)

solar_profile = solar_profile * 1527 # scaling for the required total generation
ax[0][1].plot(solar_profile[4752:4800])  # plotting a single day for the whole of Kennington
ax[0][1].set_ylabel("kWh")
ax[0][1].set_xlabel("Half hourly period")
ax[0][1].set_title("Daily PV Generation Required")

load_profile = load_profile * 1695 # scaling for the total consumption
ax[0][0].plot(load_profile[4752:4800])  # plotting a single day for the whole of Kennington
ax[0][0].set_ylabel("kWh")
ax[0][0].set_xlabel("Half hourly period")
ax[0][0].set_title("Daily Electricity Load")

# calculate the aggregated net load (i.e. annual deficit); hopefully we can compensate this with batteries
annual_net_demand = load_profile.sum() - solar_profile.sum()
print("Annual net demand: {:.2f} kWh".format(annual_net_demand)) #1,666.60 MWh

# calculate the half-hourly net load and plot
nondispatchable_net_load = load_profile - solar_profile
ax[1][0].plot(nondispatchable_net_load[4752:4800])
ax[1][0].set_ylabel("kWh")
ax[1][0].set_xlabel("Half hourly period")
ax[1][0].set_title("Daily Net Load")

# pracitcal batter storage using data from the Toyota Prius IV Plug-in (2016 model) 
## capacity is 8.8 KWh; assuming the all-electric range to be approximately 40 Km at 60 Km/h this corresponds to a power rating of 13.2 KW
energy_capacity = 8.8                                                    # kWh
power_capacity = 13                                                      # kW
eff = 0.9

energy_capacity = energy_capacity * 1415 # scaling for the total possible number of EVs i.e. one per house owning at least one car
power_capacity = power_capacity * 1415 # I'm not 100% sure if I am allowed to do this!

T = len(nondispatchable_net_load)
outpute = np.zeros((T,1))
soce = np.zeros((T,1))

for j in range(T):
    if j == 0:
        socval = energy_capacity
    else:
        socval = soce[j-1]

    if nondispatchable_net_load[j] > 0: 
        outpute[j] = min(power_capacity*0.5, nondispatchable_net_load[j], eff*socval)
        soce[j] = socval - (1/eff)*outpute[j]
        
    elif nondispatchable_net_load[j] < 0: 
        outpute[j] = max(-power_capacity*0.5, nondispatchable_net_load[j],
              -(1/eff)*(energy_capacity - socval))
        soce[j] = socval - eff*outpute[j]
        
    elif nondispatchable_net_load[j] == 0: 
        soce[j] = socval

# calculate final system net load
net_loade = nondispatchable_net_load - outpute
        
# plot battery profiles
ax[1][1].plot(soce[4752:4800], label='Practical EV Batteries')
ax[1][1].set_xlabel('Half hourly period')
ax[1][1].set_ylabel('kWh')
ax[1][1].set_title('State of Charge in the EV Battery Network')

# plotting net load, including the battery network
labels = ['PV Generation', 'Battery Operation']
 
p1 = ax[2][0].stackplot(np.arange(48), solar_profile[4752:4800].T, outpute[4752:4800].T, labels=labels, alpha=0.5)
p2 = ax[2][0].plot(load_profile[4752:4800], '-k', label='Load')
p3 = ax[2][0].plot(net_loade[4752:4800], '--k', label='Net load, inc battery network')

ax[2][0].set_xticks([0,12,24,36,48])
ax[2][0].set_xticklabels(['00:00','06:00','12:00','18:00','00:00'])
ax[2][0].set_ylabel('kWh', color='k')
ax[2][0].set_xlabel('Time', color='k')
ax[2][0].set_title('Putting it all together...')
ax[2][0].legend(loc='upper left')

# show graphs
plt.show()