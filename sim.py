#libs
import math
import random
import sys
import config
import csv
from io import StringIO

from cow_sim import Cow_simulator
from financial_models import Financial_model
from price import Price_model
from standard_sim import Standard_sim
from parser import Parser

# TODO:
# make cml tool
# extend capabilities
# make a boilerplate.py that is copyable to make more models
# make more models

if not sys.argv[1]:
   print("missing a amount of cycles as first argument and a amount invested as second argument as array")
if not sys.argv[2]:
   print("amount of cycles should be the first argument, and missing a amount invested as second argument as array")

new_sim = Cow_simulator()
fin_mod = Financial_model(new_sim)
std_sim = Standard_sim(new_sim)


res = std_sim.all_vars_analysis(Cow_simulator, 3, 50, 200, 1, 10, [], True)
print(res)
