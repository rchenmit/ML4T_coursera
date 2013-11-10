'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Example tutorial code.
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

print "Pandas Version", pd.__version__


def simulate(start_date, end_date, symbols, allocations):
    #START DATE
    #END DATE
    #SYMBOLS FOR EQUITIES
    #ALLOCATIONS
    
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    # Keys to be read from the data, it is good to read everything in one go.
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, keys)
    d_data = dict(zip(keys, ldf_data))

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values

    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]


    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_normalized_price.copy()

    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_rets) ### CHANGE THIS!!

    #ADD 1 TO na_rets
    na_rets = na_rets + 1

    #calculate standard deviation of returns
    std_rets = range(na_rets.shape[1])
    for c in range(na_rets.shape[1]):
        column = na_rets[:,c]
        col_mean = column.mean()
        col_std = column.std()
        std_rets[c] = col_std

    #calculate average daily return of TOTAL portfolio
    total_daily_ret = na_rets[:,1].copy() #placeholder for the daily return of TOTAL portfolio
    numdays = len(range(na_rets.shape[0]))
    for c in range(na_rets.shape[0]):
    #find the total return for that day
        if c==0:
            total_ret_today_percent = 0
        else:
            na_rets_today = na_rets[c,:]
            na_rets_yesterday = na_rets[c-1,:]
            total_ret_today_dollars = sum(allocations*(na_rets_today - na_rets_yesterday))
            total_value_yesterday =   sum(allocations*(na_rets_yesterday))
            total_ret_today_percent = total_ret_today_dollars / total_value_yesterday

        total_daily_ret[c] = total_ret_today_percent


    average_daily_ret = np.mean(total_daily_ret)
    std_daily_ret = np.std(total_daily_ret)
    cum_return = sum(total_daily_ret)
    sharpe_ratio =  numdays*average_daily_ret/ std_daily_ret  #sharpe ratio


    return std_daily_ret, average_daily_ret, sharpe_ratio, cum_return
    

def optimal_allocation( dt_start, dt_end, ls_symbols ):
    max_sharpe = -1
    max_alloc = [0.0, 0.0, 0.0, 0.0]
    for i in range(0,11):
        for j in range(0,11-i):
            for k in range(0,11-i-j):
                for l in range (0,11-i-j-k):
                    if (i + j + l + k) == 10:
                        alloc = [float(i)/10, float(j)/10, float(k)/10, float(l)/10]
                        vol, daily_ret, sharpe, cum_ret = simulate( dt_start, dt_end, ls_symbols, alloc )
                        if sharpe > max_sharpe:
                            max_sharpe = sharpe
                            max_alloc = alloc
    return max_alloc

def print_simulate( dt_start, dt_end, ls_symbols, ls_allocation ):
        vol, daily_ret, sharpe, cum_ret  = simulate( dt_start, dt_end, ls_symbols, ls_allocation )
        print "Start Date: ", dt_start
        print "End Date: ", dt_end
        print "Symbols: ", ls_symbols
        print "Optimal Allocations: ", ls_allocation
        print "Sharpe Ratio: ", sharpe
        print "Volatility (stdev): ", vol
        print "Average Daily Return: ", daily_ret
        print "Cumulative Return: ", cum_ret


##Example 1
dt_start = dt.datetime(2010,1,1)
dt_end = dt.datetime(2010,12,31)
ls_symbols = ['$SPX', 'KO', 'AAPL', 'HNZ']
ls_allocation = [0.0, 0.0, 0.0, 1.0]

best_alloc = optimal_allocation(dt_start, dt_end, ls_symbols)
print_simulate(dt_start, dt_end, ls_symbols, ls_allocation)


