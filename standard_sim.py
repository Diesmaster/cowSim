# todo:
# standardization var names
# standardization func names

from functools import reduce
import types
import datetime
from price import Price_model

#util funcs
def get_funcs_with_filter(obj, str_filter):
	ret = []
	for name in dir(obj): 
		if callable(getattr(obj, name)) and name[:len(str_filter)] == str_filter:
			ret.append(getattr(obj, name))

	return ret

def create_sum_of_func(obj, func_array):

	result = reduce(lambda acc, f: f(acc), func_array)

	return result


def create_copy_func(obj_old, exception): 
	new_obj = type(obj_old)()

	for name in dir(obj_old):
		result = exception.get(name)
		if not name[:2] == "__" and not name[:5] == "event":
			if not result ==  None:
				if not result == '': 
					setattr(new_obj, name, result)
			elif callable(getattr(obj_old, name)):
				#for some reason it still keeps poking in the og object / messing up the header
				value =  types.MethodType(getattr(obj_old, name), new_obj)
				#setattr(new_obj, name, value) 
			else:
				value = getattr(obj_old, name)
				setattr(new_obj, name, value) 
	    	
	Standard_sim(new_obj)
	return new_obj

def get_attr_with_filter(obj, str_filter):
	ret = []
	for name in dir(obj): 
		if name[:len(str_filter)] == str_filter:
			ret.append(getattr(obj, name))

	return ret

class Standard_sim:
	def __init__(self, sim):
		self.sim = sim

		#create std funcs

		#get_cost_montly prefix needed for every montly cost in the sim
		self.get_cost_monthly_funcs = get_funcs_with_filter(sim, 'get_cost_montly')
		self.get_revenue_montly_funcs = get_funcs_with_filter(sim, 'get_revenue_montly')

		self.sim.get_total_cost_monthly = create_sum_of_func(sim, self.get_cost_monthly_funcs)
		self.sim.get_total_revenue_monthly = create_sum_of_func(sim, self.get_revenue_montly_funcs)

		self.sim.copy_self = create_copy_func

		self.sim.check_sanity = lambda sim: True if sim.amount_balance > 0 else False

		self.make_pass_month()
		
		self.sim.max_var_all_else_equal = self.make_max_var_all_else_equal()

		self.sim.run_sim = self.make_run_sim() 

		### Make the pass month func
		#copy_base = types.MethodType(self.sim.event_pass_month_start.effect, None)

	def make_run_sim(self):
		def run_sim(amount_cycles, change_con=None, change_func=None, verbose=False):
			amount_used = 0
			amount_cycles_max = 0
			total_return = 0
			res = {}
			ret = []

			for x in range(0, int(amount_cycles*self.sim.cycle_length)):
				if self.sim.amount_cows == 0:
					test = self.sim.amount_balance
				
				if (not change_con == None) and (not change_func == None):
					if change_con() == True:
						res = change_func()
					
						if verbose == True: 
							ret.append(res)
					
						return res

				#if self.max_var_all_else_equal("amount_cows_to_buy", 0, self.amount_max_capacity) > self.amount_change_to_cycle_strat:
				#	res = self.run_sim_cycle_strat( int(amount_cycles-(x/self.cycle_length)), 12)

				#	if verbose == True: 
				#		ret.append(res)
				#	return res

				res = self.sim.pass_month()
				if verbose == True: 
					ret.append(res)

				self.sim.n_month +=1

				#if self.bool_financials == True:
				#    if not res['financials'] == '':
				#        print(res)

			if verbose == True:  
				print(self)

			self.sim.event_month_final_sell_cows.effect()

			if verbose == True:
				return ret 
			return res

		return run_sim

	def get_update_prices_funct(self):
		arr = get_attr_with_filter(self.sim, 'price_')
		
		def push_month_prices(sim):
			for obj in arr:
				if isinstance(obj, Price_model):
					obj.push_month()

		return push_month_prices



	def make_pass_month(self):
		#creation of pass month automatically
		#takes in the std logic and looks for all events that need checking in that period
		event_pass_month_start_funcs = self.filter_func_from_obj_array(get_attr_with_filter(self.sim, 'event_month_start_'), 'test_trigger')
		event_pass_month_middle_funcs = self.filter_func_from_obj_array(get_attr_with_filter(self.sim, 'event_month_middle_'), 'test_trigger')
		event_pass_month_end_funcs = self.filter_func_from_obj_array(get_attr_with_filter(self.sim, 'event_month_end_'), 'test_trigger')
		event_pass_month_final_funcs = self.filter_func_from_obj_array(get_attr_with_filter(self.sim, 'event_month_final_'), 'test_trigger')

		self.sim.event_pass_month_start.effect = self.wrap_around(event_pass_month_start_funcs, self.sim.event_pass_month_start.effect, self.sim.check_sanity)
		self.sim.event_pass_month_middle.effect = self.wrap_around(event_pass_month_middle_funcs, self.sim.event_pass_month_middle.effect, self.sim.check_sanity)
		#update prices funct
		pric_update_func = self.get_update_prices_funct()
		self.sim.event_pass_month_end.effect = self.wrap_around(event_pass_month_end_funcs, self.sim.event_pass_month_end.effect, pric_update_func)
		self.sim.event_pass_month_final.effect = self.wrap_around(event_pass_month_final_funcs, self.sim.event_pass_month_final.effect, self.sim.check_sanity)

		month_arr = [self.sim.event_pass_month_start.effect, self.sim.event_pass_month_middle.effect, self.sim.event_pass_month_end.effect, self.sim.event_pass_month_final.effect]
		
		if hasattr(self.sim, "pass_month") == True:
			self.sim.pass_month = self.wrap_around(month_arr, self.sim.pass_month, self.sim.check_sanity)
		else:
			self.sim.pass_month = self.wrap_around(month_arr, lambda: None, self.sim.check_sanity)


	def make_max_var_all_else_equal(self):
		def max_var_all_else_equal(name, n_start, n_max, n_step_size=1):
			exit = False

			while exit == False:
				n_start += n_step_size

				if n_start >= n_max:
						n_start = n_max
						exit = True
						return n_start

				#create a new sim
				new_sim = self.sim.set_stage(self.sim, 0, self.sim.amount_balance, self.sim.cycle_start)
				setattr(new_sim, name, n_start)

				#loop forward for 1 cycle
				for x in range(0, int(self.sim.cycle_length)):
					#print(n_start)

					res = new_sim.pass_month()

					new_sim.n_month +=1
					if not res['error'] == '':
						exit = True

			return n_start

		return max_var_all_else_equal

	def filter_func_from_obj_array(self, arr, str_filter):
		ret = []
		for obj in arr:
			ret = ret + get_funcs_with_filter(obj, str_filter)
		return ret

	def wrap_around(self, arr, logic, arr_check):
		def test():
			for func in arr:
				func()
			res = logic()
			if arr_check(self.sim) == False:
				#print("somewhere here it becomes insolvent")
				return {'error':'somewhere here it becomes insolvent'}
			if res == None:
				return self.sim.get_sim_return_obj()				
			return res

		return test


		# init
		# name stuff
		# return init




		# This object will assume the provided sim has properties
		# n_month
		# amount_balance
		# cycle_length
		# amount_cycles
		# money_invested
    

		# This object will assume the provided sim has functions
		# Pass/push month
		# 
		#self.get_cost_monthly_fucslambda obj_new, obj_old: setattr(obj_new, name, getattr(obj_old, name))