# this produces a CSV file with 365*48 data points which are the non-domestic demand profile in kW scalled to Kennginton's total demand

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import pickle
import datetime
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

non_domestic_load_df = pd.read_csv('data/ProfileClass3.csv') 

non_dom_daily_load = non_domestic_load_df['Aut Wd'].values
#non_dom_daily_load = [1:48]
print(non_dom_daily_load.shape)

i = 1
non_dom_annual_load = non_dom_daily_load

while i <= 5:
    non_dom_annual_load = np.concatenate((non_dom_annual_load,non_dom_daily_load), axis=None) 
    i += 1

print(non_dom_annual_load.shape)
