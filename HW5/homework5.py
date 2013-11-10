## Comp Inv HW5
## edited by rchen - Nov 10, 2013

import pandas as pd
import numpy as np
import math
import copy
import csv
import scipy as s
import sys
import matplotlib.pyplot as plt #need this in order to plot things
from pylab import * # need this for savefig()

import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep




## inputs: change these!
s_symbol_to_lookup = 'GOOG'
dt_start = dt.datetime(2010, 1, 1) #modify start dates if need be
dt_end = dt.datetime(2010, 12, 31)
i_lookback_days = 20 #number of trading days to lookback, for calculating rolling mean


## main script starts here
#get timestamps for all days, AND for the 20 days before start
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16)) ##all the timestamps for end-of-day on TRADING days --> there should be 504 days
ldt_timestamps_daysbefore_start = du.getNYSEdays( dt_start-dt.timedelta(days=i_lookback_days + 2*i_lookback_days/3), dt_start-dt.timedelta(days=1), dt.timedelta(hours=16))
ldt_timestamps_with_daysbefore_start = ldt_timestamps_daysbefore_start[-i_lookback_days:] + ldt_timestamps

##specify which symbols (sp5002012 vs sp5002008)
s_indexList = ['sp5002012'] ##looking at stocks in sp500 in 2012, applied to the time period 2008-2009 ##not sure what the piont of this is - ask Professor!!

##read in the data from Yahoo
dataobj = da.DataAccess('Yahoo')

##symbols of interest
ls_symbols = []
ls_symbols.append(s_symbol_to_lookup)

##put the relevant data into dataframe: ldf_data, and then zip it into a dictionary: d_data
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldf_data = dataobj.get_data(ldt_timestamps_with_daysbefore_start, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

## this will remove NAN from price data (which we got from S&P 500, for 2008 and 2012
for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method='ffill')
    d_data[s_key] = d_data[s_key].fillna(method='bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)


## bollinger calculation
#df_bollinger_stats = calculate_bollinger(s_symbol_to_lookup, d_data, dt_start, dt_end,  i_lookback_days)


#finding the dataframe with info for the symbol of interest 
df_close = d_data['close']
df_actualclose = d_data['actual_close']
ts_symbol_closing_prices = df_close[s_symbol_to_lookup]

# Time stamps for alldates including the 20 days before start date
ldt_timestamps_all = df_close.index
ldt_timestamps_timeframe = df_close.index[i_lookback_days:]
df_close_timeframe = df_close.ix[ldt_timestamps_timeframe]

#lists for the bollinger stuff
lf_averages = []
lf_sd = []
lf_sd_one_below = []
lf_sd_one_above = []

#calculate the rolling mean -- NOTE: its more efficient to do this with pd.rolling_mean! see TA solution!
####for i in range(i_lookback_days,len(ldt_timestamps_all)):
####    trailing_avg = np.mean(df_close[s_symbol_to_lookup][i-i_lookback_days:i+1])
####    trailing_sd = np.std(df_close[s_symbol_to_lookup][i-i_lookback_days:i+1])
####    lf_averages.append(trailing_avg)
####    lf_sd.append(trailing_sd)
####    lf_sd_one_below.append(trailing_avg - trailing_sd)
####    lf_sd_one_above.append(trailing_avg + trailing_sd)

#calculate rolling mean using pd.rolling_mean and pd.rolling_std
lf_averages = pd.rolling_mean(df_close_timeframe[s_symbol_to_lookup], 20)
lf_sd = pd.rolling_std(df_close_timeframe[s_symbol_to_lookup], 20)
lf_sd_one_below = [sum(x) for x in zip (lf_averages, -lf_sd)]
lf_sd_one_above = [sum(x) for x in zip (lf_averages, +lf_sd)] 


d_boll = {'moving_avg': lf_averages,
          'sd_one_below': lf_sd_one_below,
          'sd_one_above': lf_sd_one_above }

df_bollinger = pd.DataFrame(d_boll, index = ldt_timestamps_timeframe)

#calculate INDICATOR variable for above/below 1-sd for the bollinger 
df_prices = df_close_timeframe[s_symbol_to_lookup]
lf_bollinger_val = (df_close_timeframe - lf_averages) / (lf_sd) ##careful! df_prices is a pandas dataframe; you cannot elt-wise add two lists like this!


## Output Part 1: make the plot - price, bollinger bands, moving average
plt.clf()
plt.plot(df_bollinger.index, df_bollinger['moving_avg'])
plt.plot(df_bollinger.index, df_bollinger['sd_one_below'])
plt.plot(df_bollinger.index, df_bollinger['sd_one_above'])
plt.plot(ldt_timestamps_timeframe, df_close_timeframe[s_symbol_to_lookup], label=s_symbol_to_lookup)
plt.ylabel('Adjusted close', size='xx-small')
plt.xlabel('Date', size='xx-small')
plt.legend(['Moving average: ' + s_symbol_to_lookup, 'Avg - 1 SD', 'Avg + 1 SD'], 'Close price: ' + s_symbol_to_lookup, loc='best')
plt.xticks(size='xx-small')
plt.yticks(size='xx-small')
savefig(s_symbol_to_lookup + '_close_bollinger_' + str(dt_start) + '_' + str(dt_end) + '.pdf', format='pdf')


## Output Part 2: make the plot - price , and the -1/+1 SD cutoff; taken from TA solution
# Plotting the prices with x-axis=timestamps
plt.clf()
plt.subplot(211)
plt.plot(ldt_timestamps_timeframe, df_close_timeframe[s_symbol_to_lookup], label=s_symbol_to_lookup)
plt.legend(loc='best')
plt.ylabel('Price')
plt.xlabel('Date')
plt.xticks(size='xx-small')
plt.xlim(ldt_timestamps_timeframe[0], ldt_timestamps_timeframe[-1])
plt.subplot(212)
plt.plot(ldt_timestamps_timeframe, lf_bollinger_val, label = s_symbol_to_lookup + '-Bollinger')
plt.axhline(1.0, color='r')
plt.axhline(-1.0, color='r')
plt.legend(loc='best')
plt.ylabel('Bollinger')
plt.xlabel('Date')
plt.xticks(size='xx-small')
plt.xlim(ldt_timestamps_timeframe[0], ldt_timestamps_timeframe[-1])
plt.savefig('homework5.pdf', format='pdf')



