import math
import config
import standard_sim

class Financial_model:
	def __init__(self, sim):
		self.sim = sim

		#first it gets itself in order
		self.arr_NAV = []
		self.total_FCF = 0
		self.total_CFO = 0
		self.arr_FCF = []
		self.arr_CFO = []
		self.last_CFO = 0;
		self.arr_EARNINGS = []
		self.money_invested = self.sim.amount_money_invested

		#personal finance consts:
		self.percentage_own = config.fin_mod_config.percentage_own

		#fix the sim
		self.sim.fin_mod = self
		
		self.fix_data_gatthering()

		#self.get_assets()

		self.sim.asset_finance_funcs = self.get_calculate_cost_per_asset()


	def wrap_around(self, arr, logic, arr_check):
		def test():
			for func in arr:
				res = func()

			ret = logic()

			for arr_c in arr_check:
				res = arr_c()				
			return ret

		return test


	def fix_data_gatthering(self):
		self.sim.event_pass_month_start.effect = self.wrap_around([self.gather_data_start], self.sim.event_pass_month_start.effect, [])
		self.sim.event_pass_month_middle.effect = self.wrap_around([self.gather_data_middle], self.sim.event_pass_month_middle.effect, [])
		self.sim.event_pass_month_end.effect = self.wrap_around([self.gather_data_end], self.sim.event_pass_month_end.effect, [])
		self.sim.event_pass_month_final.effect = self.wrap_around([], self.sim.event_pass_month_final.effect, [self.gather_data_final])

		return True

	#util
	def __str__(self):
		arr_vars = [var_name for var_name in dir(self) if var_name.startswith("arr_")]
		string = ""
		for var_name in arr_vars:
			var_value = getattr(self, var_name)
			string = string + ", " + var_name + "=" + str(var_value) 
		return string

	def sum_array_until(self, arr, index):
		sum_arr = 0

		if len(arr) < index:
			index = len(arr)

		for x in range(0, index):
			sum_arr += arr[x]
			#print(sum_arr)

		return sum_arr

	def get_assets(self):
		#res = standard_sim.get_attr_with_filter(self.sim, 'amount_asset')
		res  = []
		str_filter = 'amount_asset'
		for name in dir(self.sim): 
			if name[:len(str_filter)] == str_filter:
				res.append(name)

		return res

	#start stdized funcs

	def get_calculate_cost_per_asset(self):
		assets = self.get_assets()
		func = []

		for asset in assets:
			def calculate_cost_asset():
				asset_name = asset
				asset_obj = getattr(self.sim, asset_name)
				#cost
				cost = self.sim.amount_start_balance - self.sim.amount_end_balance
				cost_per_asset = cost / asset_obj.last

				#profit
				profit = self.sim.amount_balance - self.sim.amount_start_balance
				profit_per_asset = profit / asset_obj.last

				#margin
				margin_per_asset = (profit_per_asset/cost_per_asset)*100
				annualized_IRR_per_asset = (((margin_per_asset/100)+1)**(12/self.sim.cycle_length))*100

				return { 'cost_total_' + asset_name:cost, 'cost_per_'+ asset_name:cost_per_asset, 'profit_total_'+ asset_name:profit, 'profit_per_'+ asset_name:profit_per_asset, 'margin_'+ asset_name:margin_per_asset, 'annualized_IRR_'+ asset_name:annualized_IRR_per_asset }

			func.append(calculate_cost_asset)

		return func

	def get_financials_per_cycle(self):
		if self.sim.n_month % self.sim.cycle_length == self.sim.cycle_length-1:
			financials = self.get_end_financials()
			self.sim.financials_per_cycle.append(financials)
			return financials
		else:
			return ''

	def get_end_financials(self):
		ret = { 'assets':[]}
		for func in self.sim.asset_finance_funcs:
			res = func()
			ret['assets'].append(res)

		ret['valuations'] = self.get_value_models_final()

		return ret


	#gather data
	def gather_data_final(self):
		self.arr_FCF.append(self.get_this_month_FCF(self.sim))
		self.arr_NAV.append(self.asset_based_valuation(self.sim)['NAV'])
		self.arr_EARNINGS.append(self.get_earnings(self.sim))

	def gather_data_end(self):
		return True

	def gather_data_middle(self):
		return True

	def gather_data_start(self):
		self.arr_CFO.append(self.get_this_month_CFO(self.sim))

	#Discounted Cash Flow Analysis
	def discounted_cashflow_analysis(self, discount):
		one_year_discount_amount = (100-discount)/100
		
		model_FCF = self.calculate_DCA_from_array(self.arr_FCF, one_year_discount_amount)

		model_CFO = self.calculate_DCA_from_array(self.arr_CFO, one_year_discount_amount)

		return {"FCF":model_FCF, "CFO":model_CFO}

	def calculate_DCA_from_array(self, arr, one_year_discount_amount):
		ret = []
		for index, value in enumerate(arr):
			discounted = self.calc_discount(value, one_year_discount_amount, index)
			total = self.sum_array_until(arr, index) + discounted
			ret.append(total)
		return ret

	def calc_discount(self, value, one_year_discount_amount, months):
		if months > 0: 
			return value*(one_year_discount_amount**(1+months/12))
		else:
			return value

	def get_this_month_FCF(self, sim):
		FCF = 0

		if sim.amount_balance > self.total_FCF:
			FCF = sim.amount_balance - self.total_FCF
			self.total_FCF += FCF
		else:
			for index, FCF_arr in enumerate(self.arr_FCF):
				
				if FCF_arr > sim.amount_balance:
					self.arr_FCF[index] = 0 #sim.amount_balance
					self.total_FCF -= FCF_arr

			self.total_FCF += FCF 
			

		return FCF

	def get_this_month_CFO(self, sim):
		CFO = 0
		if sim.amount_balance > self.total_CFO:
			CFO = sim.amount_balance - self.last_CFO
			self.total_CFO = sim.amount_balance
		else:
			CFO = 0

		self.last_CFO = sim.amount_balance
		return CFO

	#Earnings Multiples
	def get_earnings(self, sim):
		earnings = (sim.amount_balance - sim.amount_start_balance)
		if earnings > 0:
			return earnings
		else:
			return 0

	def earnings_multiple_analysis(self, multiple):
		ret = []
		last_earning = 0
		for index, value in enumerate(self.arr_EARNINGS):
			if not value == 0:
				cutoff = index - 11 
				if cutoff < 0:
					cutoff = 0
				
				ret.append((value + self.sum_array_until(self.arr_EARNINGS[cutoff:], 10))*multiple)
				last_earning = (value + self.sum_array_until(self.arr_EARNINGS[cutoff:], 10))*multiple
			else:
				ret.append(last_earning)

		return {"EMA":ret}


	#Asset-Based Valuation
	def asset_based_valuation(self, sim):
		NAV = sim.amount_balance + (sim.amount_cow_weight * float(sim.price_per_kg_normal))
		return {'NAV':NAV}

	def get_NAV(self):
		return {'NAV':self.arr_NAV}

	def get_value_models(self, multiple=1.2, one_year_discount_amount=6.5):
		NAV = self.get_NAV()
		EMA = self.earnings_multiple_analysis( multiple)
		DCF = self.discounted_cashflow_analysis( one_year_discount_amount)
		return {**NAV, **EMA, **DCF}

	def get_value_models_final(self, multiple=1.2, one_year_discount_amount=6.5):
		NAV = {}
		NAV = self.get_NAV()
		NAV['NAV'] = NAV['NAV'][len(NAV['NAV'])-1]

		EMA = {}
		EMA = self.earnings_multiple_analysis(multiple)
		EMA['EMA'] = EMA['EMA'][len(EMA['EMA'])-1]
		
		DCF = {}
		DCF = self.discounted_cashflow_analysis(one_year_discount_amount)
		DCF['FCF'] = DCF['FCF'][len(DCF['FCF'])-1]
		DCF['CFO'] = DCF['CFO'][len(DCF['CFO'])-1] 
		return {**NAV, **EMA, **DCF}

	def get_personal_financials(self, multiple=1.2, one_year_discount_amount=6.5):
		NAV1 = self.get_NAV()
		NAV = {}
		NAV['Valuation'] = NAV1['NAV'][len(NAV1['NAV'])-1]*(self.percentage_own/100)
		NAV['IRR'] = ((NAV1['NAV'][len(NAV1['NAV'])-1]*(self.percentage_own/100)/self.money_invested)-1)*100
		NAV['IRR_AVR_Y'] = ((NAV['IRR']/100 + 1)**(1/(len(NAV1['NAV'])/12))-1)*100
		EMA1 = self.earnings_multiple_analysis( multiple)
		EMA = {}
		EMA['Valuation'] = EMA1['EMA'][len(EMA1['EMA'])-1]*(self.percentage_own/100)
		EMA['IRR'] = ((EMA1['EMA'][len(EMA1['EMA'])-1]*(self.percentage_own/100)/self.money_invested)-1)*100
		EMA['IRR_AVR_Y'] = ((EMA['IRR']/100 + 1)**(1/(len(EMA1['EMA'])/12))-1)*100
		DCF1 = self.discounted_cashflow_analysis(one_year_discount_amount)
		FCF = {}
		FCF['Valuation'] = DCF1['FCF'][len(DCF1['FCF'])-1]*(self.percentage_own/100)
		FCF['IRR'] = ((DCF1['FCF'][len(DCF1['FCF'])-1]*(self.percentage_own/100)/self.money_invested)-1)*100
		FCF['IRR_AVR_Y'] = ((FCF['IRR']/100 + 1)**(1/(len(DCF1['FCF'])/12))-1)*100
		DFO = {} 
		DFO['Valuation'] = DCF1['CFO'][len(DCF1['CFO'])-1]*(self.percentage_own/100)
		DFO['IRR'] = ((DCF1['CFO'][len(DCF1['CFO'])-1]*(self.percentage_own/100)/self.money_invested)-1)*100
		DFO['IRR_AVR_Y'] = ((DFO['IRR']/100 + 1)**(1/(len(DCF1['CFO'])/12))-1)*100

		return {'personal':{'NAV':NAV, 'EMA':EMA, 'FCF':FCF, 'DFO':DFO}}

