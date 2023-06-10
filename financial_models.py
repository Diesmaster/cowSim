import math

class Financial_model:
	def __init__(self):
		self.arr_NAV = []
		self.total_FCF = 0
		self.total_CFO = 0
		self.arr_FCF = []
		self.arr_CFO = []
		self.last_CFO = 0;
		self.arr_EARNINGS = []

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

		return sum_arr
	
	#gather data
	def gather_data_end(self, sim):
		self.arr_NAV.append(self.asset_based_valuation(sim)['NAV'])
		self.arr_EARNINGS.append(self.get_earnings(sim))

	def gather_data_mid(self, sim):
		self.arr_FCF.append(self.get_this_month_FCF(sim))

	def gather_data_begin(self, sim):
		self.arr_CFO.append(self.get_this_month_CFO(sim))

	#Discounted Cash Flow Analysis
	def discounted_cashflow_analysis(self, sim, discount):
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

	def earnings_multiple_analysis(self, sim, multiple):
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
		NAV = sim.amount_balance + (sim.amount_cow_weight * sim.get_price_of_meat(sim.n_month))
		return {'NAV':NAV}

	def get_NAV(self):
		return {'NAV':self.arr_NAV}

	def get_value_models(self, sim, multiple=1.2, one_year_discount_amount=6.5):
		NAV = self.get_NAV()
		EMA = self.earnings_multiple_analysis(sim, multiple)
		DCF = self.discounted_cashflow_analysis(sim, one_year_discount_amount)
		return {**NAV, **EMA, **DCF}

	def get_value_models_final(self, sim, multiple=1.2, one_year_discount_amount=6.5):
		NAV = self.get_NAV()
		NAV['NAV'] = NAV['NAV'][len(NAV['NAV'])-1]
		EMA = self.earnings_multiple_analysis(sim, multiple)
		EMA['EMA'] = EMA['EMA'][len(EMA['EMA'])-1]
		DCF = self.discounted_cashflow_analysis(sim, one_year_discount_amount)
		DCF['FCF'] = DCF['FCF'][len(DCF['FCF'])-1]
		DCF['CFO'] = DCF['CFO'][len(DCF['CFO'])-1] 
		return {**NAV, **EMA, **DCF}


