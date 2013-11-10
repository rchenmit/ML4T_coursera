'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 23, 2013

@author: Sourabh Bajaj, edited by RC Nov 3, 2013
@contact: sourabhbajaj@gatech.edu
@summary: Event Profiler Tutorial

'''


import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


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
            ##HW 2 part 2: Create an event study profile of a specific "known" event on S&P 500 stocks, and compare its impact on two groups of stocks.
            ##The event is defined as when the actual close of the stock price drops below $5.00, more specifically, when:
            ##  price[t-1] >= 5.0
            ##  price[t] < 5.0
            if (f_symprice_actualclose_today < 5.0) & (f_symprice_actualclose_yest >= 5.0): ##NOTE: use ADJUSTED_CLOSE!
                df_events[s_sym].ix[ldt_timestamps[i]] = 1 ## modify the df_events matrix to say that an event happened
    return df_events


if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16)) ##all the timestamps for end-of-day on TRADING days --> there should be 504 days
    
    ##specify which symbols (sp5002012 vs sp5002008)
    s_indexList = ['sp5002012','sp5002008'] ##looking at stocks in sp500 in 2012, applied to the time period 2008-2009 ##not sure what the piont of this is - ask Professor!!

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
        print "Creating Study"
        ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                    s_filename='MyEventStudy_'+ilist+'.pdf', b_market_neutral=True, b_errorbars=True,
                    s_market_sym='SPY')





''' OUTPUT: -------------------------------------------------------------------------
>>> ls_keys
['open', 'high', 'low', 'close', 'volume', 'actual_close']

>>> len(ldt_timestamps)
504

>>> ldf_data
[<class 'pandas.core.frame.DataFrame'>      
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00  ##OPEN
Columns: 502 entries, A to SPY
dtypes: float64(502), <class 'pandas.core.frame.DataFrame'>             
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00  ##HIGH
Columns: 502 entries, A to SPY
dtypes: float64(502), <class 'pandas.core.frame.DataFrame'>             
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00  ##LOW
Columns: 502 entries, A to SPY
dtypes: float64(502), <class 'pandas.core.frame.DataFrame'>             
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00  ##CLOSE
Columns: 502 entries, A to SPY
dtypes: float64(502), <class 'pandas.core.frame.DataFrame'>             
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00  ##VOLUME; ex: ldf_data[4]['AAPL']
Columns: 502 entries, A to SPY
dtypes: float64(502), <class 'pandas.core.frame.DataFrame'>             
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00  ##ACTUAL_CLOSE
Columns: 502 entries, A to SPY
dtypes: float64(502)]

>>> ldf_data[4]['AAPL']                 ##this is the pandas data frame for VOLUME of AAPL
2008-01-02 16:00:00     38542100
2008-01-03 16:00:00     30073800
2008-01-04 16:00:00     51994000
2008-01-07 16:00:00     74006900
2008-01-08 16:00:00     54422000
2008-01-09 16:00:00     64781500
2008-01-10 16:00:00     52963400
2008-01-11 16:00:00     44010200
2008-01-14 16:00:00     39301800
2008-01-15 16:00:00     83688500
2008-01-16 16:00:00     79065900
2008-01-17 16:00:00     62780700
2008-01-18 16:00:00     61583700
2008-01-22 16:00:00     86955500
2008-01-23 16:00:00    120463200
...
2009-12-09 16:00:00    24456500
2009-12-10 16:00:00    17488200
2009-12-11 16:00:00    15349100
2009-12-14 16:00:00    17706800
2009-12-15 16:00:00    14980700
2009-12-16 16:00:00    12606600
2009-12-17 16:00:00    13887100
2009-12-18 16:00:00    21741800
2009-12-21 16:00:00    21853800
2009-12-22 16:00:00    12482700
2009-12-23 16:00:00    12340200
2009-12-24 16:00:00    17888900
2009-12-28 16:00:00    23020200
2009-12-29 16:00:00    15900200
2009-12-30 16:00:00    14717300
Name: AAPL, Length: 504

>>> d_data['volume']['AAPL']            ##this is the DICTIONARY form of the last output, for VOLUME of AAPL
2008-01-02 16:00:00     38542100
2008-01-03 16:00:00     30073800
2008-01-04 16:00:00     51994000
2008-01-07 16:00:00     74006900
2008-01-08 16:00:00     54422000
2008-01-09 16:00:00     64781500
2008-01-10 16:00:00     52963400
2008-01-11 16:00:00     44010200
2008-01-14 16:00:00     39301800
2008-01-15 16:00:00     83688500
2008-01-16 16:00:00     79065900
2008-01-17 16:00:00     62780700
2008-01-18 16:00:00     61583700
2008-01-22 16:00:00     86955500
2008-01-23 16:00:00    120463200
...
2009-12-09 16:00:00    24456500
2009-12-10 16:00:00    17488200
2009-12-11 16:00:00    15349100
2009-12-14 16:00:00    17706800
2009-12-15 16:00:00    14980700
2009-12-16 16:00:00    12606600
2009-12-17 16:00:00    13887100
2009-12-18 16:00:00    21741800
2009-12-21 16:00:00    21853800
2009-12-22 16:00:00    12482700
2009-12-23 16:00:00    12340200
2009-12-24 16:00:00    17888900
2009-12-28 16:00:00    23020200
2009-12-29 16:00:00    15900200
2009-12-30 16:00:00    14717300
Name: AAPL, Length: 504

>>> d_data
{'volume': <class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00
Columns: 502 entries, A to SPY
dtypes: float64(502), 'high': <class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00
Columns: 502 entries, A to SPY
dtypes: float64(502), 'low': <class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00
Columns: 502 entries, A to SPY
dtypes: float64(502), 'actual_close': <class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00
Columns: 502 entries, A to SPY
dtypes: float64(502), 'close': <class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00
Columns: 502 entries, A to SPY
dtypes: float64(502), 'open': <class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 504 entries, 2008-01-02 16:00:00 to 2009-12-30 16:00:00
Columns: 502 entries, A to SPY
dtypes: float64(502)}

'''
