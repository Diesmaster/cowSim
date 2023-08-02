# todo:
# standardization var names
# standardization func names

from functools import reduce
import types

import config

from price import Price_model
from asset import Asset

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
		if not name[:2] == "__" and not name[:5] == "event" and not name[:5] == "price" and not name[:7] == "fin_mod" and not name[:13] == "amount_asset_":
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
		elif name[:13] == "amount_asset_":
			asset_obj = getattr(obj_old, name)
			setattr(new_obj, name, Asset(asset_obj.amount, asset_obj.last, asset_obj.to))
		elif name[:5] == "price":
			asset_obj = getattr(obj_old, name)
			setattr(new_obj, name, Price_model(asset_obj.get_price(), max_up=asset_obj.max_up, max_down=asset_obj.max_down, distribution=asset_obj.distribution, n_per_year=asset_obj.n_per_year))
	    	
	Standard_sim(new_obj)
	return new_obj

def get_attr_with_filter(obj, str_filter):
	ret = []
	for name in dir(obj): 
		if name[:len(str_filter)] == str_filter:
			ret.append(getattr(obj, name))

	return ret

def copy_when_prefix(obj, other, prefix):
	for pre in prefix:
		for name in dir(other):
			if name[:len(pre)] == pre:
				if name[: (len(pre) + len("asset_"))] == (pre + "asset_"):
					amount_asset = getattr(other, name)
					setattr(self, name, Asset(amount_asset.amount, amount_asset.last, amount_asset.to))
				else:
					setattr(self, name, getattr(other, name))

def add_when_prefix(obj, other, prefix):
	for pre in prefix:
		for name in dir(other):
			if name[:len(pre)] == pre:
				if name[: (len(pre) + len("asset_"))] == (pre + "asset_"):
					amount_asset = getattr(other, name)
					obj_asset = getattr(obj, name)
					setattr(obj, name, Asset(amount_asset.amount + obj_asset.amount, amount_asset.last + obj_asset.last, amount_asset.to + obj_asset.to))
				else:
					setattr(obj, name, getattr(other, name)+getattr(obj, name))

def load_config(new_obj, name):
    obj = getattr(config, name)
    ret = []
    for name in dir(obj): 
        if not name[:2] == "__":
            attr = getattr(obj, name)
            setattr(new_obj, name, attr)

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

		self.sim.__eq__ = self.get_eq_func()

		self.sim.__add__ = self.get_add_func()


	def get_config_vars(self):
		obj = getattr(config, self.sim.config_name)
		config_vars = dir(obj)

		vars = {}
		for var_name in config_vars:
			if not var_name.startswith("__"):  # Exclude built-in variables
				var_value = getattr(obj, var_name)
				vars[var_name] = var_value
    
		return vars

	def all_vars_analysis(self, sim_type, amount_of_increments, min_perc, max_perc, time_frame, n_experiment, filter_list, verbose=False):
		vars = self.get_config_vars()

		print(vars)

		res = {}

		for var in filter_list:
			vars.pop(var)

		for key in vars:
			std_value = vars[key]
			min_amount = std_value*(min_perc/100)
			max_amount = std_value*(max_perc/100)

			res[key] = self.var_analysis(sim_type, key, min_amount, max_amount, amount_of_increments, time_frame, n_experiment, verbose)

		return res

	def var_analysis(self, sim_type, config_var_name, min, max, amount_of_increments, time_frame, n_experiment, verbose=False):
		if verbose  == True:
			print("we are going to test the effect of var: " + str(config_var_name) + " by running the simulation over domain: " + str(min) + ", " + str(max))

		obj = getattr(config, self.sim.config_name)
		std_value = getattr(obj, config_var_name)
	
		if verbose  == True:
			print("the standard value is: " + str(std_value) + ", " + "the time frame is: " + str(time_frame) + " cycles")
	  
		diff = max - min 
		incr_size = diff/amount_of_increments

		ret = []

		for x in range(0, amount_of_increments):
			res = []

			for n in range(0, n_experiment):
				value = min + (x*incr_size)

				setattr(obj, config_var_name, value)
				new_sim = sim_type()
				std_sim = Standard_sim(new_sim)

				res.append(new_sim.run_sim(time_frame))          
				res[n]['value'] = value

			err = 0
			balance = 0
			for result in res:
				if not result['error'] == '':
					err += 1
				else:
					balance += result['balance']
	    
			res = {'error':err/n_experiment, 'balance':balance/(n_experiment-err), 'value':res[0]['value']}
			ret.append(res)
	    
		if verbose  == True:
			print("run " + str(x) + " is finsihed, with " + str(config_var_name) + ": " + str(value))

		return ret


	def make_run_sim(self):
		def run_sim(amount_cycles, change_con=None, change_func=None, verbose=False):
			amount_used = 0
			amount_cycles_max = 0
			total_return = 0
			res = {}
			ret = []

			for x in range(0, int(amount_cycles*self.sim.cycle_length)):
				if (not change_con == None) and (not change_func == None):
					if change_con() == True:
						res = change_func()
					
						if verbose == True: 
							ret.append(res)
							print(self)
						return res

				res = self.sim.pass_month()
				if verbose == True: 
					ret.append(res)

				self.sim.n_month +=1

				if not res['error'] == '':
					print(self.sim)
					return res

			if verbose == True:  
				print(self)

			end_balance = self.sim.amount_end_balance
			self.sim.event_month_final_sell_cows.effect()
			self.sim.amount_end_balance = end_balance

			if verbose == True:
				return ret 
			return res

		return run_sim
	
	def get_eq_func(self):
		
		start = ['amount_', 'n_']
		
		def eq_func(og, other):
			copy_when_prefix(og, other, start)
			return og 

		return eq_func

	def get_add_func(self):
		start = ['amount_']

		def add_func(og, other):
			add_when_prefix(og, other, start)
			return og

		return add_func


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
				new_sim = self.sim.set_stage(self.sim, 0, self.sim.amount_balance*((100-self.sim.n_buffer)/100), self.sim.n_cycle_start)
				if name[:13] == "amount_asset_":
					asset_obj = getattr(self.sim, name)
					setattr(new_sim, name, Asset(asset_obj.amount, asset_obj.last, n_start))
				
				else:		
					setattr(new_sim, name, n_start)

				#loop forward for 1 cycle
				for x in range(0, int(self.sim.cycle_length)):
					#print(n_start)

					res = new_sim.pass_month()

					new_sim.n_month +=1
					#print("month: " + str(self.sim.n_month) + ", self: " + str(self.sim))
					if not res['error'] == '':
						exit = True

			return n_start-2

		return max_var_all_else_equal

	def filter_func_from_obj_array(self, arr, str_filter):
		ret = []
		for obj in arr:
			ret = ret + get_funcs_with_filter(obj, str_filter)
		return ret

	def wrap_around(self, arr, logic, arr_check):
		def test():
			for func in arr:
				res = func()

				err = None
				if type(res) == type({}):
					err = res.get('error')
				if not (err == None) and not (err == '') :
					return {'error':'somewhere here it becomes insolvent'}
			res = logic()
			if arr_check(self.sim) == False:
				#print("somewhere here it becomes insolvent")
				return {'error':'somewhere here it becomes insolvent'}
			if res == None:
				return self.sim.get_sim_return_obj()				
			return res

		return test