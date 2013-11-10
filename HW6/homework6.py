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
import copy as cp
import csv
import scipy as s
import sys
import math
import matplotlib.pyplot as plt 
from pylab import * 

import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep




## functions -- copied from HW4/homework4.py
def find_events_bollinger(ls_symbols, df_bollinger):
    ''' Finding the event dataframe '''
    ts_market = df_bollinger['SPY']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = cp.deepcopy(df_bollinger)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_bollinger.index


    
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp

            f_bollinger_sym_today = df_bollinger[s_sym].ix[ldt_timestamps[i]]
            f_bollinger_sym_yest = df_bollinger[s_sym].ix[ldt_timestamps[i-1]]
            f_bollinger_market_today = df_bollinger['SPY'].ix[ldt_timestamps[i]]
            f_bollinger_market_yest = df_bollinger['SPY'].ix[ldt_timestamps[i-1]]

            ##HW 6: Create an event study profile of a specific "known" event on S&P 500 stocks, and compare its impact on two groups of stocks.
            '''
            HW6 event study:
                Bollinger value for the equity today <= -2.0
                Bollinger value for the equity yesterday >= -2.0
                Bollinger value for SPY today >= 1.0
            '''
            if (f_bollinger_sym_today <= -2.0 and f_bollinger_sym_yest >= -2.0 and f_bollinger_market_today >= 1.0):
                df_events[s_sym].ix[ldt_timestamps[i]] = 1 ## modify the df_events matrix to say that an event happened
                             
    return df_events

def event_profiler(ldt_timestamps, ls_symbols):
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    ls_symbols = c_dataobj.get_symbols_from_list(s_symbols_for_events)
    ls_symbols.append('SPY')

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Copying close price into separate dataframe to find rets
    df_close = d_data['close']
    df_mean = pd.rolling_mean(d_data['close'], 20)
    df_std = pd.rolling_std(d_data['close'], 20)

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    #bollinger
    df_bollinger = (df_close - df_mean) / (df_std)
    print df_bollinger.tail()


    print "Creating Event Study"
    df_events = find_events_bollinger(ls_symbols, df_bollinger)

    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='EventStudy_Bollinger' + '.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')



## MAIN
##input:
# Start and End date of the charts
dt_start = dt.datetime(2008, 1, 1)
dt_end = dt.datetime(2009, 12, 31)

# We need closing prices so the timestamp should be hours=16.
dt_timeofday = dt.timedelta(hours=16)

# Get a list of trading days between the start and the end.
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

# do it for S&P 2012 symbol list
s_symbols_for_events = 'sp5002012'

event_profiler(ldt_timestamps, s_symbols_for_events)







