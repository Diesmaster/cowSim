#libs
import math
import random
import sys
import config
from cow_sim import Cow_simulator


#todo
#meat price eid ul adha calculations
#more cycling styles
#more in-depth feed price when above 100 cattle

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




if not sys.argv[1]:
   print("missing a amount of cycles as first argument and a amount invested as second argument as array")
if not sys.argv[2]:
   print("amount of cycles should be the first argument, and missing a amount invested as second argument as array")

investment = [150000000, 150000000, 0, 150000000]

new_sim = Cow_simulator(investment[0])

#optimal_time_frame(1, 20, 150000000, 10)

err = new_sim.run_sim_cycle_strat( int(sys.argv[1]) + 1, 4, [investment[0]], True )

#err = new_sim.run_sim( int(sys.argv[1]), [investment[0]], True )