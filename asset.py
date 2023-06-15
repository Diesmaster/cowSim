

class Asset:
	def __init__(self, amount=0, last=0, to=0):
		#amount right now
		self.amount = amount

		#last buy
		self.last = last

		#future buy
		self.to = to