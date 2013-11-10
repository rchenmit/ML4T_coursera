#!/bin/bash

python Homework7_TAsol.py #this generates orders.csv
python marketsim.py 100000 orders.csv marketsim_fundvalue_TA_soln.csv #this generates market_sim_fundvalue.csv
python analyze_soln_mod_hw4.py marketsim_fundvalue_TA_soln.csv SPY
