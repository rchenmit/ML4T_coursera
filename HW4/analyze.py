## computational investing 1 - HW3, part 2
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


## functions

#read in the CSV file,which has the columns: year, month, day, fundvalue
def _read_in_csv(filename):
    inputfile = open(filename, 'rU')
    reader = csv.reader(inputfile, delimiter=',')

    dates = []
    fundvalues = []
    for row in reader:
        year = int(row[0])
        month = int(row[1])
        day = int(row[2])
        value = float(row[3])
        date = dt.datetime(year, month, day, 16) #add 16 hours for closing time!!
        dates.append(date)
        fundvalues.append(value)
    #save as a timeseries!
    ts_fundvalues = pd.TimeSeries( dict(zip(dates, fundvalues))) #zip the tuples of (date, fundvalue), and convert the zip into a dict
    inputfile.close()
    return ts_fundvalues

#read in the benchmark data from our DataAccess('Yahoo')
def _read_bench(symbol, timestamps):
    dataobj = da.DataAccess('Yahoo')
    close = dataobj.get_data(timestamps, [symbol], "close", verbose=True)
    close = close.fillna(method='ffill')
    close = close.fillna(method='bfill')
    return close[symbol]

## main script
# parameters 
#csv_input_filename = 'market_sim_fundvalue.csv'
#input_benchmark = 'SPY' 
csv_input_filename = sys.argv[1]
input_benchmark = sys.argv[2]

# read in the data
ts_fundvalues = _read_in_csv(csv_input_filename) #timeseries with value of our fund
start_date = ts_fundvalues.index[0]
end_date = ts_fundvalues.index[-1]

#ts_benchmark_values = _read_in_benchmark(input_benchmark, list(ts_fundvalues.index)) #read in the benchmark closing prices for the same timestamps as ts_fundvalues
ts_benchmark_values = _read_bench(input_benchmark, list(ts_fundvalues.index))


##
##dataobj = da.DataAccess('Yahoo') #data from yahoo
##close = dataobj.get_data(list(ts_fundvalues.index), ['SPY'], ['Close']) #pass a list of symbols to da.get_data
##close = close.fillna(method='ffill')
##close = close.fillna(method='bfill')
##ts_benchmark_values = pd.TimeSeries( dict(zip(list(ts_fundvalues.index), close['SPY'])))
####



# calculate charpe ratios
daily_fund_rets = tsu.daily(ts_fundvalues)
daily_benchmark_rets = tsu.daily(ts_benchmark_values)
sharpe_fund = tsu.get_sharpe_ratio(daily_fund_rets)[0] #note the tsu.get_sharpe_raio returns an ARRAY of ONE value (sharpe ratio)
sharpe_benchmark = tsu.get_sharpe_ratio(daily_benchmark_rets)[0]
std_fund = np.std(daily_fund_rets, axis = 0)[0] #numpy.std returns an ARRAY, so take the 0th elt in the array
std_benchmark = np.std(daily_benchmark_rets, axis = 0)[0]
avg_dailyret_fund = np.mean(daily_fund_rets, axis = 0)[0]
avg_dailyret_benchmark = np.mean(daily_benchmark_rets, axis = 0)[0]

print 'The final value of the portfolio using the sample file is: ' , ts_fundvalues.index[-1], ': $' , ts_fundvalues[-1]
print "Details of the performance of the portfolio: "
print "Data range: ", start_date, " to " , end_date
print "Sharpe Ratio of fund: ", sharpe_fund
print "Sharpe Ratio of Benchmark: ", input_benchmark, ": ", sharpe_benchmark
print "Standard Deviation of Fund :  ", std_fund
print "Standard Deviation of $SPX : ", std_benchmark
print "Average Daily Return of Fund :  ", avg_dailyret_fund
print "Average Daily Return of $SPX : ", avg_dailyret_benchmark




