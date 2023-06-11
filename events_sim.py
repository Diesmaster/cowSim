
class Event_sim():
	def __init__(self, condition, effect):
		self.condition = condition
		self.effect = effect

	def test_trigger(self):
		if self.condition() == True:
			return self.effect()