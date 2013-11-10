## computational investing 1 , week 6 - HW4
## edited by rchen - Nov 6, 2013
##
#### In this homework you will take the output of your Event Study work to
#### build a more complete back testing platform. Specifically, you should
#### choose an event from the ones you have experimented with in this class,
#### assess it and tune it using the Event Profiler, then back test it with
#### the simulator you created.

import pandas as pd
import numpy as np
import math
import copy
import csv
import scipy as s

import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep


## functions
def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['close']
    df_actualclose = d_data['actual_close']
    ts_market = df_close['SPY']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    #ouptut file to write events:
    csv_outfile = open('orders.csv', 'wb')
    writer = csv.writer(csv_outfile, delimiter=',')
    
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_symprice_actualclose_today = df_actualclose[s_sym].ix[ldt_timestamps[i]]
            f_symprice_actualclose_yest = df_actualclose[s_sym].ix[ldt_timestamps[i-1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]] #.ix is for *mixed* INTEGER and Label (NaN's in this case)
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            '''
            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
            if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
            '''
            ##HW 4: Create an event study profile of a specific "known" event on S&P 500 stocks, and compare its impact on two groups of stocks.
            ##The event is defined as when the actual close of the stock price drops below $5.00, more specifically, when:
            ##  price[t-1] >= 5.0
            ##  price[t] < 5.0
            i_numshares_buy = 100
            f_price_cutoff = 5.0

            if (f_symprice_actualclose_today < f_price_cutoff):
            #if (f_symprice_actualclose_today < f_price_cutoff) & (f_symprice_actualclose_yest >= f_price_cutoff): ##NOTE: use ADJUSTED_CLOSE!
                df_events[s_sym].ix[ldt_timestamps[i]] = 1 ## modify the df_events matrix to say that an event happened
                ## WRITE a string to an output file like this:
                ## Date, AAPL, BUY, 100
                ## Date + 5 days, AAPL, SELL, 100
                row_to_write_buy = [str(ldt_timestamps[i].year), str(ldt_timestamps[i].month), str(ldt_timestamps[i].day), \
                                s_sym, 'Buy', i_numshares_buy]
                writer.writerow(row_to_write_buy)
                try:
                    time_sell = ldt_timestamps[i+5] #this makes it 5 TRADING DAYS (not calendar days); because ldt_timestamps holds the trading days
                except:
                    time_sell = ldt_timestamps[-1] #use the last timestamp if there are less than 5 trading days after timestamp i
                row_to_write_sell = [str(time_sell.year), str(time_sell.month), str(time_sell.day), \
                                s_sym, 'Sell', i_numshares_buy]
                writer.writerow(row_to_write_sell)

    csv_outfile.close()# close the writer
                
    return df_events

## main script
if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1) #modify start dates if need be
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16)) ##all the timestamps for end-of-day on TRADING days --> there should be 504 days
    
    ##specify which symbols (sp5002012 vs sp5002008)
    s_indexList = ['sp5002012'] ##looking at stocks in sp500 in 2012, applied to the time period 2008-2009 ##not sure what the piont of this is - ask Professor!!

    ##read in the data from Yahoo
    dataobj = da.DataAccess('Yahoo')

    ##lookup for both 2008 and 2012 S&P
    for ilist in s_indexList:
        
        ls_symbols = dataobj.get_symbols_from_list(ilist)
        ls_symbols.append('SPY')

        ##put the relevant data into dataframe: ldf_data, and then zip it into a dictionary: d_data
        ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
        ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
        d_data = dict(zip(ls_keys, ldf_data))

        ## this will remove NAN from price data (which we got from S&P 500, for 2008 and 2012
        for s_key in ls_keys:
            d_data[s_key] = d_data[s_key].fillna(method='ffill')
            d_data[s_key] = d_data[s_key].fillna(method='bfill')
            d_data[s_key] = d_data[s_key].fillna(1.0)

        df_events = find_events(ls_symbols, d_data)

