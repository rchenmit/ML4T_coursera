## computational investing 1 - HW3
## market simulator
## edited by rchen - Nov 6, 2013

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


## Functions
##read in CSV file -- for this exercise, use the CSV files they gave us on HW3 page!
##this will return an array: trades
def read_csv_to_df(filename):
    reader = csv.reader(open(filename, 'rU'), delimiter=',')
    dates = np.array([]) #all the dates
    orderdata = []
    print "reading in the raw data: ---------------------- \n"
    for row in reader:
        year = int(row[0])
        month = int(row[1])
        day = int(row[2])
        sym = row[3]
        action = row[4]
        volume = int(row[5])
        
        dates = np.append(dates, dt.datetime(year, month, day) + dt.timedelta(hours=16))  #add the date
        orderdata.append([sym, action, volume])
    
    #create pandas dataframe with timestamps and order data
    df_orders = pd.DataFrame(orderdata, index=dates, columns=['sym', 'action', 'volume'])
    return df_orders
        

## Main script! -----------------------------------------------------------------------------
i_start_cash = 1000000
csv_input = './orders_outoforder.csv' # read in CSV file and print it out
csv_output = './market_sim_fundvalue.csv' #output file

## STEP 1 (from instructions in compinvesting1-PDF-MLT Simulator.pdf
df_orders = read_csv_to_df(csv_input).sort() ##pandas dataframe; read in using function i wrote above; sort the Pandas dataframe by index(date) after its read in
# get a list of all dates (removing duplicates) and all symbols traded (removing duplicates)
dt_start = min(df_orders.index)
dt_end = max(df_orders.index)
ls_dt_all_from_orders = df_orders.index.tolist()
sym_all_from_orders = df_orders['sym'].tolist()
#remove duplicate syms, dates
ls_sym_unique = list(set(sym_all_from_orders))
ls_dt_unique = list(set(ls_dt_all_from_orders))
ls_dt_unique.sort()


## STEP 2 -- put this into a function!
#read in the data from Yahoo
dataobj = da.DataAccess('Yahoo')
dt_start_read = dt_start
dt_end_read = dt_end + dt.timedelta(days=1) #end date needs to be offset by one
ldt_timestamps = du.getNYSEdays(dt_start_read, dt_end_read,  dt.timedelta(hours=16))
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldf_data = dataobj.get_data(ldt_timestamps, ls_sym_unique, ls_keys)
d_data = dict(zip(ls_keys, ldf_data)) #this is the data for the symbols we're interested in
#remove the NaNs from the price data
for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method='ffill')
    d_data[s_key] = d_data[s_key].fillna(method='bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)

## STEP 3
#dataframe for SHARES of each symbol that you are CURRENTLY HOLDING- make sure they are floating point numbers!
df_trade_matrix = np.zeros((len(ldt_timestamps), len(ls_sym_unique)))
df_trade_matrix = pd.DataFrame(df_trade_matrix, index = ldt_timestamps, columns = ls_sym_unique)
##df_trade_matrix = pd.DataFrame(index=ldt_timestamps, columns=ls_sym_unique)
##df_trade_matrix = df_trade_matrix.fillna(0) # with 0s rather than NaNs
##df_trade_matrix = df_trade_matrix.sort()

#fill the dataframe for shares to add (for each trade) of each symbol (df_trade_matrix)
#do this by iterating through the orders (df_orders) and filling the number of shares for that particular symbol and date
for date, row in df_orders.iterrows():
    if row['action'] == 'Buy':
        shares_add = int(row['volume'])
    elif row['action'] == 'Sell':
        shares_add = -1*int(row['volume'])
    else:
        next
    symbol = row['sym']
    df_trade_matrix.loc[date][symbol] += float(shares_add)
    

## STEP 4
# create a timeseries for CASH - tells you what your CASH VALUE is (starting cash + any buy/sell you've made)
#df_cash = pd.DataFrame( s.zeros(len(ls_dt_unique)), ls_dt_unique, columns=['CASH'])
ts_cash = pd.TimeSeries( 0.0, ldt_timestamps)
ts_cash[0] = i_start_cash

# for each order, subtract the cash used in that trade
# need to multiple volume*price
df_close = d_data['close']

for date, row in df_trade_matrix.iterrows():
##    for sym in df_trade_matrix.columns:
##        price = df_close[sym].ix[date]
##        print price, sym
##        s_cash.loc[date] -= price * df_trade_matrix.loc[date][sym] #update the cash SPENT
    ##use dot product - faster than nested for loop (commented above this line)

    cash = np.dot(row.values.astype(float), df_close.ix[date].values)
    ts_cash[date] -= cash


## STEP 5
# append '_CASH' into the price data; df_close['_CASH'] = 1.0
df_trade_matrix['_CASH'] = ts_cash
df_trade_matrix = df_trade_matrix.cumsum() #fills forward with the current shares you're holding (this is the HOLDING MATRIX)
# calculate teh fund value with the price matrix and the holding matrix
historic = df_close
historic['_CASH']=1
ts_fundvalue = pd.TimeSeries(0.0, df_close.index)
for date, row in df_trade_matrix.iterrows():
    ts_fundvalue[date] += np.dot(row.values.astype(float), df_close.ix[date].values)

## STEP 6
# write the ts_fundvalue to a CSV file!
csv_file = open(csv_output, 'wb') #open the CSV file
writer = csv.writer(csv_file, delimiter=',')
for row_index in ts_fundvalue.index:
    row_to_write = [str(row_index.year), str(row_index.month), \
                    str(row_index.day), str(ts_fundvalue[row_index])]
    writer.writerow(row_to_write)
csv_file.close() #close the CSV file!!!



