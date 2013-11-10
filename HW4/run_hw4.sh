#!/bin/bash

python homework4.py #this generates orders.csv
python market_simulator_for_hw4.py orders.csv #this generates market_sim_fundvalue.csv
python analyze_soln_mod_hw4.py market_sim_fundvalue.csv SPY 
