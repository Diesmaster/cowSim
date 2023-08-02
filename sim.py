#libs
import math
import random
import sys
import config
import csv
import importlib
import json
from io import StringIO


#from cow_sim import Cow_simulator
from financial_models import Financial_model
from price import Price_model
from standard_sim import Standard_sim
from parser import Parser

# TODO:
# make a boilerplate.py that is copyable to make more models
# fix parser
# add inflation
# make more models
# expand capabilities

res = {}

def get_substring_until_char(input_string, target_char):
    index = input_string.find(target_char)
    if index != -1:
        return input_string[:index]
    else:
        return input_string

def sim_import( name ):
  file_name = name 
  
  class_name = get_substring_until_char(name, '_') + "_simulator"
  class_name = class_name.capitalize()

  sim_class =  imported_module = importlib.import_module(file_name)
  sim_class = getattr(sim_class, class_name) 
  return sim_class

if len(sys.argv) < 1:
   print("missing the fuction and sim")
   exit()
if len(sys.argv) < 2:
   print("missing either the function or the sim")
   exit()

chosen_sim = sim_import(sys.argv[2])

new_sim = chosen_sim()
fin_mod = Financial_model(new_sim)
std_sim = Standard_sim(new_sim)


if sys.argv[1] == "run":
  if len(sys.argv) < 3:
    print("missing the amount of cycles")
    exit()

  options = sys.argv

  #change able cons for that func
  verbose = False

  for option in options:
    if option == '-v':
       verbose = True      
  

    elif option == "-h":
       print("args: amount of cycles")
       exit()


  res = new_sim.run_sim(int(sys.argv[3]), verbose=verbose)

elif sys.argv[1] == "var_analysis":
  options = sys.argv

  #change able cons for that func
  verbose = False

  for option in options:
    if option == '-v':
       verbose = True      
  

    elif option == "-h":
       print("args: amount_of_increments, min_perc, max_perc, amount_of_cycles, n_experiment, filter_list (as string) ")
       exit()

  if len(sys.argv) < 7:
    print("missing arguments, try -h")
    exit()  
data
  amount_of_increments =  int(sys.argv[3])
  min_perc = int(sys.argv[4]) 
  max_perc = int(sys.argv[5])
  amount_of_cycles =  int(sys.argv[6])
  n_experiment = int(sys.argv[7])
  filter_list = json.loads(sys.argv[8])

  res = std_sim.all_vars_analysis  ( chosen_sim, amount_of_increments, min_perc, max_perc, amount_of_cycles, n_experiment, filter_list, verbose)
  

print(res)
# pars = Parser()
# res = pars.dict_to_csv_parser(res)
# print(res)