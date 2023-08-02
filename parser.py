from io import StringIO

import csv

class Parser():
	# JSON to csv data
	def flatten_dict(self, data, new_key=''):
		#flattened_data = []

		"""if type(data) == type({}):
			res = {}

			for key, value in data.items():
				if type(value) == type({}) or type(value) == type([]):
					if not new_key == "":
						key = new_key + "_" + key

					res1 = self.flatten_dict(value, key)
					
					if type(res1) == type([]):
						res[key] = res1
					else:
						res = {**res, **res1}
				else:
					
					if not new_key == "":
						name = new_key +  "_" + key
					else:
						name = key
					res[name] = value

			return res
		



		elif type(data) == type([]):
			ret = []
			for item in data:
				res = self.flatten_dict(item, new_key)
				print(new_key + ", " + str(res) )
				ret.append(res)
				return ret
"""
		flattened_dict = {}
		for key, value_list in data.items():
		    for idx, value_dict in enumerate(value_list):
		        for inner_key, inner_value in value_dict.items():
		            new_key = f"{key}_{idx}_{inner_key}"
		            flattened_dict[new_key] = inner_value
		
		return flattened_dict

	def extract_keys(self, array):
	    keys = set()
	    for dictionary in array:
	        keys.update(dictionary.keys())
	    return list(keys)

	def dict_to_csv_parser(self, data):
		"""data = self.flatten_dict(data) # get out 1 to 1 relations
		final_data = ""
		keys = []

		print("\n")
		print(data)
		print("\n")

		#print headers
		for key, value in data[0].items():
			if final_data == "":
				final_data = key
			else:
				final_data = final_data + "," + key

			keys.append(key)

		final_data = final_data + "\n"

		#print data
		#for array in data:
		#	for key in keys:

		#		value = array.get(key)
		#		
		#		final_data = final_data  + "," + str(value)

		#	final_data = final_data + "\n"
			"""

		print(data)

		csv_buffer = StringIO()
		#writer = csv.writer(csv_buffer)
		writer = csv.DictWriter(csv_buffer, fieldnames=data.keys())
		writer.writeheader()
		writer.writerows(data)
		csv_string = csv_buffer.getvalue()
		csv_buffer.close()
		return csv_string
		

	def res_to_data(self, res, list_wants):
		ret = None
		if type(res) == type({}):
			ret = {}
			for key, value in res.items():
				pass_on = {}
				pass_on[key] = value
		
				for want in list_wants:
					if want == key:
						ret[key] = value

					ret1 = self.res_to_data(value, list_wants)
				if not ret1 == {}:    
					ret[key] = self.res_to_data(value, list_wants)

				return ret
		elif type(res) == type([]):
			ret = []
			for value in res: 
				ret.append(self.res_to_data(value, list_wants))
			return ret
		else:
			return {}
		return ret