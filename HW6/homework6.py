## Comp Inv HW6 - event study with bollinger bands
## edited by rchen - Nov 10, 2013
##
##Part 1: Implement Bollinger bands as an indicator using 20 day look back. The upper band should represent the mean plus one
##   standard deviation and the lower band is the mean minus one standard deviation. Have your code output the indicator value in
##   a range of -1 to 1. This is similar to the last homework so you have already completed that.
##Part 2: Now create an event study with the signal being:
##      Bollinger value for the equity today <= -2.0
##      Bollinger value for the equity yesterday >= -2.0
##      Bollinger value for SPY today >= 1.0
##  So we're looking for situations where the stock has punched through the lower band and the market is substantially in the
##  other direction. That suggests that something special is happening with the stock.
##Part 3: Now use the indicator you created as the part 2 of the homework 5 and create an event study to find potentially
##interesting results.


import pandas as pd
import numpy as np
import math
import copy
import csv
import scipy as s
import sys
import mat
import matplotlib.pyplot as plt 
from pylab import * 

import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep




## MAIN

## Part 1 - already completed in last HW -- using TA solution for HW5
# List of symbols
ls_symbols = ["AAPL", "GOOG", "IBM", "MSFT"]

# Start and End date of the charts
dt_start = dt.datetime(2010, 1, 1)
dt_end = dt.datetime(2010, 6, 15)

# We need closing prices so the timestamp should be hours=16.
dt_timeofday = dt.timedelta(hours=16)

# Get a list of trading days between the start and the end.
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

# Creating an object of the dataaccess class with Yahoo as the source.
c_dataobj = da.DataAccess('Yahoo')

# Keys to be read from the data, it is good to read everything in one go.
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

# Reading the data, now d_data is a dictionary with the keys above.
# Timestamps and symbols are the ones that were specified before.
ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

# Copying close price into separate dataframe to find rets
df_close = d_data['close']
df_mean = pd.rolling_mean(d_data['close'], 20)
df_std = pd.rolling_std(d_data['close'], 20)

df_bollinger = (df_close - df_mean) / (df_std)
print df_bollinger.tail()

## Part 2 
## creating event study with the signal being:
##      Bollinger value for the equity today <= -2.0
##      Bollinger value for the equity yesterday >= -2.0
##      Bollinger value for SPY today >= 1.0






