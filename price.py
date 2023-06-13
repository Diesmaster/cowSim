import math
import random


class Price_model:
	def __init__(self, base_price, exceptions={}, max_up=0, max_down=0, distribution='', n_per_year=0):
		if not exceptions == {}:
			self.price_amount = []
			for x in range(1, 13):
				self.price_amount.append(exceptions.get(str(x), base_price))
		else:
			self.price_amount = base_price

		self.n_month = 0

		if n_per_year > 0:
			self.n_per_year = n_per_year
			self.max_up = max_up
			self.max_down = max_down
			self.distribution = distribution
			self.complex_price = True

	def __int__(self):
		return int(self.get_price())

	def __float__(self):
		return float(self.get_price())

	def __mul__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			return self.get_price() * other
		else:
			raise TypeError("test Unsupported operand type")


	def __str__(self):
		return str(self.price_amount)

	def get_uniform_change(self, price):
		n_gradient  = 100
		random_number = (random.randint(self.max_down*-1*n_gradient, self.max_up*n_gradient))/n_gradient
		multiplier = (100+random_number)/100
		price = price*multiplier
		return price

	def get_normal_change(self, price):
		n_gradient  = 100
		mean = self.max_up - self.max_down
		sigma = (self.max_up + self.max_down) / 2
		#sigma = 1 
		random_number = random.gauss(mean, sigma)
		multiplier = 1 + random_number/100
		price = price*multiplier
		return price

	#these distribution treat price increases as independent events, however they are not ofc.
	#if the last month had a price increase the next month will prob also have a price increase and visa-versa
	def update_price(self):
		price = self.get_price()
		if self.distribution == 'uniform':
			price = self.get_uniform_change(price)
		elif self.distribution == 'normal':
			price = self.get_normal_change(price)
		else:
			print("distribution not in our program")
			exit()

		self.set_price(price, self.n_month)
		return True

	def push_month(self):
		if (self.n_month % (12/self.n_per_year)) == 0:
			self.update_price()
		self.n_month += 1


	def get_price(self):
		if type(self.price_amount) ==  type([]):
			return self.price_amount[self.n_month % 12]
		else:
			return self.price_amount

	def set_price(self, n, n_month=0):
		if type(self.price_amount) ==  type([]):
			for x in range(n_month+1, n_month+1+ int(12/self.n_per_year) ):
				self.price_amount[ x % 12] = n	
		else:
			self.price_amount = n