import math
import random
import sys
import config

from financial_models import Financial_model
from price import Price_model
from events_sim import Event_sim
import standard_sim


# todo
# define eq, etc for the simulator.

class Cow_simulator:

    def event_condition_buy_cows(self):
        if ((self.n_month - self.n_cycle_start) % self.cycle_length) == 0:
            #print("n_month: " + str(self.n_month) + ", cycle_start: " + str(self.cycle_start) + ", cycle_length: " + str(self.cycle_length))
            return True 
        return False

    def event_effect_buy_cows(self):
        self.amount_start_balance = self.amount_balance
        amount_used = self.amount_balance
        
        if self.amount_cows_to_buy == 0:
            self.amount_cows_to_buy = self.max_var_all_else_equal("amount_cows_to_buy", int(self.amount_cows_bought_last*0.9), self.amount_max_capacity)
        
        cost = self.calculate_cow_buy_cost(self.amount_cows_to_buy)
        self.amount_balance -= cost
        self.amount_cow_weight += self.cattle_bought_at_kg*self.amount_cows_to_buy
        self.amount_cows += self.amount_cows_to_buy
        self.amount_cows_bought_last = self.amount_cows_to_buy
        self.amount_cows_to_buy = 0

    def event_condition_sell_cows(self):
        if( (self.n_month - self.n_cycle_start) % self.cycle_length) == 2:
            return True 
        return False

    def event_effect_sell_cows(self):
        #print("month: " + str(self.n_month) + ", self: " + str(self))
        self.amount_end_balance = self.amount_balance
        revenue = self.calculate_cow_revenue_sim()
        self.amount_balance += revenue
        self.amount_cow_weight = 0
        self.amount_cows = 0

    def event_condition_change_feed(self):
        if (self.amount_cows > 100) and (self.bool_feed_change == False):
            return True
        return False

    def event_effect_change_feed(self):
        self.bool_feed_change = True
        self.price_of_concentraat = Price_model(float(self.price_of_concentraat)*((100-self.price_of_concentraat_if_gt_100_decrease)/100), max_up=1, max_down=1, distribution='normal', n_per_year=12)
        

    def event_effect_pass_month_start(self):
        if not self.fin_mod == None:
            self.fin_mod.gather_data_begin(self)
        
        return True

    def event_effect_pass_month_middle(self):
        #add cow weight
        self.amount_cow_weight += self.amount_cows*self.monthly_targeted_adg_kg_per_cattle
        return True

    def event_effect_pass_month_end(self):
        cost = self.get_total_cost_monthly()
        
        self.amount_balance -= cost

        rev = self.get_total_revenue_monthly()
        self.amount_balance += rev

        if not self.fin_mod == None:
            self.fin_mod.gather_data_mid(self)

        return True    

    def event_effect_pass_month_final(self):
        if not self.fin_mod == None:
          self.fin_mod.gather_data_end(self)        

###todo fix config load
    def __init__(self, amount_invested=config.money_invested):
        ##need in here bc cannot be put in here before init function is called
        standard_sim.load_config(self, 'cow_sim_config')

        ### prices you need to call them prices_ at the start
        self.price_per_kg_normal = Price_model(self.price_per_kg_normal, exceptions={'6':self.price_per_kg_eid}, max_up=1, max_down=1, distribution='normal', n_per_year=12)
        self.price_of_concentraat = Price_model(self.price_of_concentraat, max_up=1, max_down=1, distribution='normal', n_per_year=12)
        self.price_per_cow_250kg = Price_model(self.price_per_cow_250kg, max_up=1, max_down=1, distribution='normal', n_per_year=12)
        self.price_of_grass = Price_model(self.price_of_grass, max_up=1, max_down=1, distribution='normal', n_per_year=12)
        self.price_fermented_poop = Price_model(self.price_fermented_poop, max_up=1, max_down=1, distribution='normal', n_per_year=12)

        #events you need to call them month start/middle/end/final so the program knows where to put it
        self.event_month_middle_buy_cows = Event_sim(self.event_condition_buy_cows, self.event_effect_buy_cows)
        self.event_month_final_sell_cows = Event_sim(self.event_condition_sell_cows, self.event_effect_sell_cows)
        self.event_month_end_change_feed = Event_sim(self.event_condition_change_feed, self.event_effect_change_feed)
        
        ## std boiler plate, here you can define logic that happens every month in the specified time period 
        self.event_pass_month_start = Event_sim(None, self.event_effect_pass_month_start)
        self.event_pass_month_middle = Event_sim(None, self.event_effect_pass_month_middle)
        self.event_pass_month_end = Event_sim(None, self.event_effect_pass_month_end)
        self.event_pass_month_final = Event_sim(None, self.event_effect_pass_month_final)

        #objt vars
        #2 types of std var names n and amount
        #n is for vars that are a number but should not be added.
        # examples is current month, starting month, etc. 
        self.n_month = 0 #REQ
        self.n_cycle_start = 0 #REQ
        self.n_cycle_devider = self.cycle_length
        self.n_cycles_per_year = 0
        self.n_buffer = 10 #REQ
        self.bool_feed_change = False

        #the other type of var is amount
        #amount should be added if you have 2 farms aka 2 simulations.
        #ex: amount of cows total = cows farm 1 + cows farm 2
        self.amount_cow_weight = 0 
        self.amount_cows = 0
        self.amount_cows_to_buy = 0;
        self.amount_balance = amount_invested #REQ

        #finance vars
        self.amount_money_invested = amount_invested
        self.amount_start_balance = 0;
        self.amount_cows_bought_last = 0;
        self.amount_end_balance = 0

        self.financials_per_cycle = []
        self.fin_mod = None

    #str implementation is usr specific, what do you want to see
    def __str__(self):
       string = "Month: " + str(self.n_month) + ", Total Cow Weight: " + str(self.amount_cow_weight) + ", Amount of Cows: " + str(self.amount_cows) + ", Balance: " + str(self.amount_balance) 
       return string

    #sims interpretation of the copy function
    def set_stage(self, org_sim, cows, n_balance=-1, start=0):
        exception = {'amount_cows':cows, 'n_cycle_start':start}
        if n_balance > -1:
            exception = {**exception, 'amount_balance':n_balance}
        new_sim = org_sim.copy_self(org_sim, exception)


        return new_sim


    def set_config_value(self, var_name, new_value):
        setattr(self, var_name, new_value)
        return getattr(self, var_name)

    def import_fin_module(self, fin_mod):
        self.fin_mod = fin_mod


    #def calculations costs takes in n_cows
    def calculate_cow_buy_cost(self, n_cows):
        return n_cows * float(self.price_per_cow_250kg)

    def amount_of_dry_feed_needed_daily_sim(self):
      return self.amount_cow_weight * (self.percentage_of_dry_matter / 100)

    def amount_of_concentrate_needed_cycle_sim(self):
      return self.amount_of_dry_feed_needed_daily_sim() * (self.percentage_of_dry_matter_concentraat / 100) * (100 / self.percentage_of_concentraat_dry) * 30

    def amount_of_grass_needed_cycle_sim(self):
      return self.amount_of_dry_feed_needed_daily_sim() * (self.percentage_of_dry_matter_grass / 100) * (100 / self.percentage_of_grass_dry) * 30

    def get_cost_montly_cow_feed_sim(self):
        return self.amount_of_concentrate_needed_cycle_sim() * float(self.price_of_concentraat) + self.amount_of_grass_needed_cycle_sim() * float(self.price_of_grass)
  
    def calculate_farm_hand_sim(self):
      return math.ceil(self.amount_cows / 25) * self.cost_of_farmhand

    def calculate_security_sim(self):
      if self.amount_cows > 20:
        return 1 * self.cost_of_security_guard
      else:
        return 0

    def get_costs_monthly_labor_costs_sim(self):
      return self.calculate_farm_hand_sim() + self.calculate_security_sim()

    def calculate_total_costs_sim(self):
      return  self.get_cost_montly_cow_feed_sim() + self.get_costs_monthly_labor_costs_sim()

    def calculate_costs_min_monthly_revenue_sim(self):
      return self.get_total_cost_monthly() - self.get_total_revenue_monthly()

    #byproduct poop
    def calculate_amount_wet_poop_sim(self):
      return self.amount_of_dry_feed_needed_daily_sim() * (100 / self.percentage_poop_dry)

    def calculate_amount_fermented_poop_sim(self):
      return self.calculate_amount_wet_poop_sim() * (self.percentage_poop_fermented_weight_decrease / 100)

    def get_revenue_montly_poop_revenue_sim(self):
      return self.calculate_amount_fermented_poop_sim() * float(self.price_fermented_poop) * 30

    def calculate_cow_revenue_sim(self):
      return float(self.price_per_kg_normal)*self.amount_cow_weight

    #todo
    def cost_rent():
      return 0

    #util funcs
    def get_sim_return_obj(self):
        if self.bool_financials == False:
            return {'error':'', 'cows':self.amount_cows, 'balance':self.amount_balance}
        else:
            financials = self.get_financials_per_cycle() 
            return {'error':'', 'financials':financials, 'cows':self.amount_cows, 'balance':self.amount_balance}

























    ### financials TODO move all to financial lib
    def calculate_profit(self, amount_costs, amount_revenue):
      return amount_revenue-amount_costs 

    def calculate_balance(self, amount_costs, amount_revenue, amount_investment):
      return amount_revenue + amount_investment - amount_costs

    def calculate_total_return(self, n_cows, amount_balance):
      return self.calculate_total_costs(n_cows) + amount_balance

    def set_financials(self, financials=False):
        self.bool_financials = financials

    def calculate_final_cost_per_cow(self):
        cost = self.amount_start_balance - self.amount_end_balance
        cost_per_cow = cost/self.amount_cows_bought_last
        return cost, cost_per_cow

    def calculate_profit_per_cow(self):
        profit = self.amount_balance - self.amount_start_balance
        profit_per_cow = profit / self.amount_cows_bought_last
        return profit, profit_per_cow

    def calculate_margin(self, profit_per_cow, cost_per_cow):
        return (profit_per_cow/cost_per_cow)*100

    def calculate_annualized_IRR(self, margin):
        return (((margin/100)+1)**(12/self.cycle_length))*100

    def get_financials_per_cycle(self):
        if self.n_month % self.cycle_length == self.cycle_length-1:
            financials = self.get_end_financials()
            self.financials_per_cycle.append(financials)
            return financials
        else:
            return ''

    def get_financials(self):
        return self.financials_per_cycle

    def get_end_financials(self):
        perc_IRR = (self.amount_balance / self.amount_money_invested)*100

        cost, cost_per_cow = self.calculate_final_cost_per_cow()

        profit, profit_per_cow = self.calculate_profit_per_cow()

        margin = self.calculate_margin(profit_per_cow, cost_per_cow)

        annualized_IRR = self.calculate_annualized_IRR(margin)

        valuations = ''
        if not type(self.fin_mod) == type(None):
            valuations = self.fin_mod.get_value_models_final()
        
        
        return {"total IRR":perc_IRR, "cost_per_cycle":cost, "cost_per_cow":cost_per_cow, "profit_per_cycle":profit, "profit_per_cow":profit_per_cow, "margin":margin, "annualized_IRR":annualized_IRR, 'valuations':valuations}





















####REKT FUNCS: buys too many cows
# get this run out of this obj deze func == rekt
    def run_sim_cycle_strat(self, amount_cycles, amount_of_cycles_per_year, verbose=False):
      if amount_of_cycles_per_year > 12:
        return {'error': 'Impossible amount of cycles'}
      
      if 12 % amount_of_cycles_per_year:
        return {'error': 'Impossible amount of cycles'}

      self.n_cycles_per_year = amount_of_cycles_per_year
      #(12/length)
      self.n_cycle_devider = int(amount_of_cycles_per_year/(12/self.cycle_length))

      split = self.amount_balance/self.n_cycle_devider
      self.amount_balance = []

      sims = []

      for x in range(0, self.n_cycle_devider):
        self.amount_balance.append(split)    
        new_sim = self.set_stage(self, 0, self.n_month)
        new_sim.amount_max_capacity = self.amount_max_capacity/self.n_cycle_devider
        sims.append(new_sim)


      amount_used = 0
      amount_cycles_max = 0
      total_return = 0
      res = {}
      ret = {}

      for x in range(0, int(amount_cycles*self.cycle_length)):
        if x % self.n_cycle_devider >= len(sims):
            new_sim = self.set_stage(self, 0, self.n_month)
            sims.append(new_sim)

        self.push_pass_multiple_sims(sims)
        self.n_month += 1

        new_sim = self.add_list_to_parent(sims)

        if verbose == True:
          ret.append(new_sim)
          print(self.print_individually(sims))

      
      new_sim.event_month_final_sell_cows.effect()
      if verbose == True:
        return ret
      return new_sim.get_sim_return_obj()


    def push_pass_multiple_sims(self, sims):
        for x in range(0, len(sims)):
            res = sims[x].pass_month()
            sims[x].n_month += 1


    def add_list_to_parent(self, sims):
        if len(sims) == 1:
            return sims[0]
        elif len(sims) == 2:
            return sims[0] + sims[1]
        elif len(sims) > 2:
            new_sim = sims[0] + sims[1]
            for x in range(2, len(sims)):
                new_sim = new_sim + sims[x]

        return new_sim

    def print_individually(self, sims):
        for x in range(0, len(sims)):
            print(sims[x])
   