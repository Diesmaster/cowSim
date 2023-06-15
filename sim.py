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


#JSON to csv data
def flatten_dict(data, new_key=''):
  flattened_data = []

  if type(data) == type({}):
    res = None
    
    for key, value in data.items():

      if not new_key == '':
        key = new_key + "_" + key
      res1 = flatten_dict(value, key)
      
      if type(res1) == type({}):
        if res == None:
          res = res1
        else:
          res = { **res, **res1 }
      else:
        if res == None:
          res = [res1]
        else:
          res.append(res1)
    return res

  elif type(data) == type([]):
    ret = []
    
    for item in data:
      res = flatten_dict(item, new_key)
      ret.append(res)
    return ret
  else:
    return {new_key:data}
      

  return flattened_data

def extract_keys(array):
    keys = set()
    for dictionary in array:
        keys.update(dictionary.keys())
    return list(keys)

def dict_to_csv_parser(data):
    data = flatten_dict(data)

    csv_string = StringIO()
    
    big_array = [{}]
    for one_array in data:
      if type(one_array) == type([]) and len(one_array) > 1: 
      
        for index, small_array in enumerate(one_array):
          if len(big_array) <= index:
            big_array.append(small_array) 
          elif type(big_array[index]) == type({}):
            big_array[index] = {**big_array[index], **small_array}
          else:
            big_array[index] = small_array

        keys = extract_keys(big_array)

        writer = csv.DictWriter(csv_string, fieldnames=keys if big_array else [])

        #writer = csv.DictWriter(csv_string, fieldnames=big_array[0].keys() if big_array else [])
        writer.writeheader()
        writer.writerows(big_array)
        return csv_string.getvalue()  
      
      elif len(data) == 1:
        writer = csv.DictWriter(csv_string, fieldnames=one_array.keys() if one_array else [])
        writer.writeheader()
        writer.writerows(data)
        return csv_string.getvalue()

      else:
        writer = csv.DictWriter(csv_string, fieldnames=one_array.keys() if one_array else [])
        writer.writeheader()
        writer.writerows(one_array)
        return csv_string.getvalue()

    writer = csv.DictWriter(csv_string, fieldnames=data[0].keys() if data else [])
    writer.writeheader()
    writer.writerows(data)
    return csv_string.getvalue()

def res_to_data(res, list_wants):
  ret = None
  if type(res) == type({}):
    ret = {}
    for key, value in res.items():
      pass_on = {}
      pass_on[key] = value
      
      for want in list_wants:
        if want == key:
          ret[key] = value
      
      ret1 = res_to_data(value, list_wants)
      if not ret1 == {}:    
        ret[key] = res_to_data(value, list_wants)

    return ret
  elif type(res) == type([]):
    ret = []
    for value in res: 
      ret.append(res_to_data(value, list_wants))
    return ret
  else:
    return {}

  return ret


#sim calculations
def run2run(amount_cycles, amount_1, amount_2):
  amount_investment1 = [amount_1]
  amount_investment2 = [amount_2] 

  #how much do we pay per cow?
  #how much do we pay per cycle?

  new_sim1 = Cow_simulator(amount_1)
  new_sim2 = Cow_simulator(amount_2)

  ret1 = new_sim1.run_sim(amount_cycles, amount_investment1)
  ret2 = new_sim2.run_sim(amount_cycles, amount_investment2)

  amount_return1 = ret1['balance']/amount_investment1[0]
  amount_return2 = ret2['balance']/amount_investment2[0]

  #print("invested1: " + str(amount_investment1[0]) + ", invested2: " + str(amount_investment2[0]))
  #print("amount1: " + str(amount_return1) + ", amount2: " + str(amount_return2))
  return amount_return1, amount_return2

def optimal_investment_stratgy(amount_cycles, amount_minimum):
  amount_investment1 = amount_minimum
  amount_investment2 = amount_minimum*2 

  amount_return1, amount_return2 = run2run(amount_cycles, amount_investment1, amount_investment2)
  
  while not amount_investment1 == amount_investment2:
    if amount_return2 > amount_return1:
      amount_investment1 = amount_investment2
      amount_investment2 = amount_investment2*2

      amount_return1, amount_return2 = run2run(amount_cycles, amount_investment1, amount_investment2)
    else:
      #het optimum zit tussen amount_investment1/2 en amount_investment2
      amount_investment1 = amount_investment1/2
      amount_investment2 = amount_investment2

      amount_difference = amount_investment2 - amount_investment1


      while amount_difference > 5: 
        amount_difference = amount_investment2 - amount_investment1

        #print("difference: " + str(amount_difference), ", inv1: " + str(amount_investment1) + ", inv2: " + str(amount_investment2))

        random_number = random.randint(amount_investment1, amount_investment2)

        new_sim = Cow_simulator(random_number)

        res = new_sim.run_sim(amount_cycles, [random_number])
        
        #print("invested_res: " + str(random_number) + ", " + "return_res: " + str(res['balance']/random_number) )
        
        if random_number - amount_investment1 < amount_investment2 - random_number:
          amount_investment1 = random_number
        else:
          amount_investment2 = random_number

      amount_investment1 = amount_investment2  

  return amount_investment1 

def optimal_time_frame(amount_cycles_minimum, amount_cycles_maximum, amount_minimum, n_precision):
  for x in range(amount_cycles_minimum, amount_cycles_maximum):
    amount_invested = 0
    max_loop = n_precision
    for y in range(0,max_loop):
      amount_optimum_invest = optimal_investment_stratgy(x, amount_minimum)
      amount_invested += amount_optimum_invest
    
    print("average optimum for " + str(x) + ", invested: " + str(amount_invested/max_loop))

def var_analysis(config_var_name, min, max, amount_of_increments, time_frame, amount_invested, verbose=False):
  if verbose  == True:
    print("we are going to test the effect of var: " + str(config_var_name) + " by running the simulation over domain: " + str(min) + ", " + str(max))
  
  std_value = getattr(config, config_var_name)
  
  if verbose  == True:
    print("the standard value is: " + str(std_value) + ", " + "the time frame is: " + str(time_frame) + " cycles")
  
  diff = max - min 
  incr_size = diff/amount_of_increments

  ret = []

  for x in range(0, amount_of_increments):
    value = min + (x*incr_size)

    new_sim = Cow_simulator(amount_invested)
    
    #new_sim.set_config_value(config_var_name, value)
    setattr(new_sim, config.var_name, value)


    res = new_sim.run_sim(time_frame)
    res['value'] = value
    ret.append(res)
    
    if verbose  == True:
      print("run " + str(x) + " is finsihed, with " + str(config_var_name) + ": " + str(value))

  return ret

def get_config_vars():
    config_vars = dir(config)

    vars = {}
    for var_name in config_vars:
        if not var_name.startswith("__"):  # Exclude built-in variables
            var_value = getattr(config, var_name)
            vars[var_name] = var_value
    
    return vars

def all_vars_analysis(amount_of_increments, min_perc, max_perc, time_frame, amount_invested, filter_list, verbose=False):
  vars = get_config_vars()

  res = {}

  for var in filter_list:
    vars.pop(var)

  for key in vars:
    std_value = vars[key]
    min_amount = std_value*(min_perc/100)
    max_amount = std_value*(max_perc/100)

    res[key] = var_analysis(key, min_amount, max_amount, amount_of_increments, time_frame, investment[0], verbose)

  return res

def analize_difference(to_be_analyzed, time_frame, amount_invested, verbose=False):
  benchmark_sim = Cow_simulator(amount_invested)
  benchmark_res = benchmark_sim.run_sim( time_frame )

  res = []


  for key in to_be_analyzed:
    for x in range(0, len(to_be_analyzed[key])):
      difference_perc = (to_be_analyzed[key][x]['balance']/benchmark_res['balance'])*100
      balance_analysis = to_be_analyzed[key][x]['balance']
      balance_benchmark = benchmark_res['balance']
      value_analysis = to_be_analyzed[key][x]['value']
      res_element = {'value_analysis':value_analysis, 'difference_perc':difference_perc, 'balance_analysis':balance_analysis, 'balance_benchmark':balance_benchmark}
      print(res_element)
      res.append(res_element)

  return res


if not sys.argv[1]:
   print("missing a amount of cycles as first argument and a amount invested as second argument as array")
if not sys.argv[2]:
   print("amount of cycles should be the first argument, and missing a amount invested as second argument as array")

new_sim = Cow_simulator(int(sys.argv[2]))
fin_mod = Financial_model(new_sim)
std_sim = Standard_sim(new_sim)


res = new_sim.run_sim(int(sys.argv[1]))
print(res)
#res = fin_mod.get_end_financials()
#print(res)
