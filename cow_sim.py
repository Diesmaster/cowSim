import math
import random
import sys
import config

#todo
#more cycling styles
#more in-depth feed price when above 100 cattle

class Cow_simulator:
    def __init__(self, invested):
        self.price_per_kg_normal = config.price_per_kg_normal
        self.my_share_low = config.my_share_low
        self.percentage_of_dry_matter = config.percentage_of_dry_matter
        self.price_per_kg_eid = config.price_per_kg_eid
        self.my_share_high = config.my_share_high
        self.price_of_concentraat = config.price_of_concentraat
        self.price_of_concentraat_if_gt_100 = config.price_of_concentraat_if_gt_100
        self.price_per_cow_250kg = config.price_per_cow_250kg
        self.price_of_grass = config.price_of_grass
        self.monthly_targeted_adg_kg_per_cattle = config.monthly_targeted_adg_kg_per_cattle
        self.cost_of_farmhand = config.cost_of_farmhand
        self.cattle_bought_at_kg = config.cattle_bought_at_kg
        self.cost_of_security_guard = config.cost_of_security_guard
        self.money_invested = config.money_invested
        self.cycle_length = config.cycle_length
        self.total_daily_feed_cost = config.total_daily_feed_cost
        self.fermented_poop_price = config.fermented_poop_price
        self.wet_poop_price = config.wet_poop_price
        self.percentage_poop_dry = config.percentage_poop_dry
        self.cows_daily_poop_kg = config.cows_daily_poop_kg
        self.percentage_poop_fermented_weight_decrease = config.percentage_poop_fermented_weight_decrease
        self.percentage_of_dry_matter_concentraat = config.percentage_of_dry_matter_concentraat
        self.percentage_of_concentraat_dry = config.percentage_of_concentraat_dry
        self.percentage_of_dry_matter_grass = config.percentage_of_dry_matter_grass
        self.percentage_of_grass_dry = config.percentage_of_grass_dry
        self.amount_max_capacity = config.amount_max_capacity

        #objt vars
        self.n_month = 0
        self.amount_cow_weight = 0
        self.amount_balance = invested
        self.amount_cows = 0
        self.amount_of_cycles_per_year = 0;
        self.cycle_devider = self.cycle_length


    def __str__(self):
       string = "Month: " + str(self.n_month) + ", Total Cow Weight: " + str(self.amount_cow_weight) + ", Amount of Cows: " + str(self.amount_cows) + ", Balance: " + str(self.amount_balance) 
       return string

    def set_stage(self, month, cow_weight, cows):
        self.n_month = month
        self.amount_cow_weight = cow_weight
        self.amount_cows = cows

    def get_balance(self):
        return self.amount_balance

    #setters
    def buy_cows(self, n_cows):
       cost = self.calculate_cow_buy_cost(n_cows)
       self.amount_balance -= cost
       self.amount_cow_weight += self.cattle_bought_at_kg*n_cows
       self.amount_cows += n_cows

    def sell_cows(self, n_cows):
        revenue = self.calculate_cow_revenue_sim()
        self.amount_balance += revenue
        self.amount_cow_weight -= (self.cattle_bought_at_kg + self.monthly_targeted_adg_kg_per_cattle*self.cycle_length )*n_cows
        self.amount_cows -= n_cows

    #used to test how many cows we can buy.
    def pass_month_arg_cow(self, n_cows, verbose=False):
        if verbose == True:
            print("begin of the month: " + str(self))

        #buy the cows again beginning of month
        if(self.n_month % self.cycle_length) == 0:
            amount_used = self.amount_balance
            self.buy_cows(n_cows)

        #add cow weight
        self.amount_cow_weight += self.amount_cows*self.monthly_targeted_adg_kg_per_cattle

        #calculate costs of last month end of month
        cost = self.calculate_total_costs_sim()
        self.amount_balance -= cost

        #calculate montly profit poop
        rev = self.calculate_poop_revenue_sim()
        self.amount_balance += rev

        if self.amount_balance < 0:
            return {'error':'company becomes insolvent somewhere in this cycle'}

        #calculate total profit end of month
        if(self.n_month % self.cycle_length) == (self.cycle_length - 1):
            self.sell_cows(self.amount_cows)

        if verbose == True:
            print("end-- of the month: " + str(self))

        return {'error':'', 'cows':self.amount_cows, 'balance':self.amount_balance}


    def pass_month(self, verbose=False):
        if verbose == True:
            print("begin of the month: " + str(self))

        #buy the cows again beginning of month
        if(self.n_month % self.cycle_devider) == 0:
            amount_used = self.amount_balance
            n_cows = self.calculate_amount_of_cow_sim(0, amount_used)
            self.buy_cows(n_cows)

        #add cow weight
        self.amount_cow_weight += self.amount_cows*self.monthly_targeted_adg_kg_per_cattle

        #calculate costs of last month end of month
        cost = self.calculate_total_costs_sim()
        self.amount_balance -= cost

        #calculate montly profit poop
        rev = self.calculate_poop_revenue_sim()
        self.amount_balance += rev

        if self.amount_balance < 0:
            return {'error':'company becomes insolvent somewhere in this cycle'}

        #calculate total profit end of month
        if(self.n_month % self.cycle_devider) == (self.cycle_devider -1):
            self.sell_cows(self.amount_cows)

        if verbose == True:
            print("end-- of the month: " + str(self))

        return {'error':'', 'cows':self.amount_cows, 'balance':self.amount_balance}

    def push_month(self):
        self.n_month += 1
        

    #def calculations costs takes in n_cows
    def calculate_cow_buy_cost(self, n_cows):
        return n_cows * self.price_per_cow_250kg

    # ---- using obj vars on a montly basis ------ #

    def amount_of_dry_feed_needed_daily_sim(self):
      return self.amount_cow_weight * (self.percentage_of_dry_matter / 100)

    def amount_of_concentrate_needed_cycle_sim(self):
      return self.amount_of_dry_feed_needed_daily_sim() * (self.percentage_of_dry_matter_concentraat / 100) * (100 / self.percentage_of_concentraat_dry) * 30

    def amount_of_grass_needed_cycle_sim(self):
      return self.amount_of_dry_feed_needed_daily_sim() * (self.percentage_of_dry_matter_grass / 100) * (100 / self.percentage_of_grass_dry) * 30

    def calculate_cow_feed_cost_sim(self):
      return self.amount_of_concentrate_needed_cycle_sim() * self.price_of_concentraat + self.amount_of_grass_needed_cycle_sim() * self.price_of_grass

    def calculate_farm_hand_sim(self):
      return math.ceil(self.amount_cows / 25) * self.cost_of_farmhand

    def calculate_security_sim(self):
      if self.amount_cows > 20:
        return 1 * self.cost_of_security_guard
      else:
        return 0

    def calculate_labor_costs_sim(self):
      return self.calculate_farm_hand_sim() + self.calculate_security_sim()

    def calculate_total_costs_sim(self):
      return  self.calculate_cow_feed_cost_sim() + self.calculate_labor_costs_sim()

    def calculate_costs_min_monthly_revenue_sim(self):
      return self.calculate_total_costs_sim() - self.calculate_poop_revenue_sim()

    #byproduct poop
    def calculate_amount_wet_poop_sim(self):
      return self.amount_of_dry_feed_needed_daily_sim() * (100 / self.percentage_poop_dry)

    def calculate_amount_fermented_poop_sim(self):
      return self.calculate_amount_wet_poop_sim() * (self.percentage_poop_fermented_weight_decrease / 100)

    def calculate_poop_revenue_sim(self):
      return self.calculate_amount_fermented_poop_sim() * self.fermented_poop_price * 30

    def calculate_cow_revenue_sim(self):
      return self.amount_cow_weight * self.price_per_kg_normal[self.n_month % 12]

    def calculate_total_revenue_sim(self):
      return self.calculate_cow_revenue_sim() + self.calculate_poop_revenue_sim()

    # ---- end of overload  ----

    def calculate_amount_of_cow_sim(self, n_start, total_money):
        balance = 0
        #print(n_start)

        while balance < total_money:
            n_start += 1
            
            new_sim = Cow_simulator(total_money)
            new_sim.set_stage(self.n_month, self.amount_cow_weight, n_start)
            #print(new_sim)
            
            for x in range(0, self.cycle_length):
                res = new_sim.pass_month_arg_cow(n_start)   
                new_sim.push_month()
                if not res['error'] == '':
                    return n_start -1

            if n_start >= self.amount_max_capacity:
                return self.amount_max_capacity

        return n_start - 1

    #todo
    def cost_rent():
      return 0

    #financials

    def calculate_profit(self, amount_costs, amount_revenue):
      return amount_revenue-amount_costs 

    def calculate_balance(self, amount_costs, amount_revenue, amount_investment):
      return amount_revenue + amount_investment - amount_costs

    def calculate_total_return(self, n_cows, amount_balance):
      return self.calculate_total_costs(n_cows) + amount_balance

    #code
    def run_sim(self, amount_cycles, amount_investment, verbose=False):
      amount_used = 0
      amount_cycles_max = 0
      total_return = 0
      res = {}

      for x in range(0, amount_cycles*self.cycle_length):
        res = self.pass_month()
        self.push_month()

        if verbose == True:  
          print(self)

      self.sell_cows(self.amount_cows) 
      return res

    def run_sim_cycle_strat(self, amount_cycles, amount_of_cycles_per_year, amount_investment, verbose=False):
      if amount_of_cycles_per_year > 12:
        return {'error': 'Impossible amount of cycles'}
      
      if 12 % amount_of_cycles_per_year:
        return {'error': 'Impossible amount of cycles'}

      self.amount_of_cycles_per_year = amount_of_cycles_per_year
      self.cycle_devider = 12/amount_of_cycles_per_year

      amount_used = 0
      amount_cycles_max = 0
      total_return = 0
      res = {}

      for x in range(0, amount_cycles*self.cycle_length):
        res = self.pass_month()
        self.push_month()

        if verbose == True:  
          print(self)

      self.sell_cows(self.amount_cows) 
      return res

