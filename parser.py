class Parser():
	# JSON to csv data
	def flatten_dict(self, data, new_key=''):
		flattened_data = []

		if type(data) == type({}):
			res = None

			for key, value in data.items():

				if not new_key == '':
					key = new_key + "_" + key
					res1 = self.flatten_dict(value, key)

					if type(res1) == type({}):
						if res == None:
							res = res1
						else:
							res = { **res, **res1 }
					else:
						if res == None:
							res = [res1]
				else:
					res.append(res1)
					return res

		elif type(data) == type([]):
			ret = []

			for item in data:
				res = self.flatten_dict(item, new_key)
				ret.append(res)
				return ret
		else:
			return {new_key:data}


		return flattened_data

	def extract_keys(self, array):
	    keys = set()
	    for dictionary in array:
	        keys.update(dictionary.keys())
	    return list(keys)

	def dict_to_csv_parser(self, data):
		data = self.flatten_dict(data)

		csv_string = StringIO()

		big_array = [{}]
		for one_array in data:
			if type(one_array) == type([]) and len(one_array) > 1: 

				for index, small_array in enumerate(one_array):
					if len(big_array) <= index:
						big_array.append(small_array) 
					elif type(big_array[index]) == type({}):
						big_array[index] = {**big_array[index], **small_array}
					else:
						big_array[index] = small_array

					keys = self.extract_keys(big_array)

					writer = csv.DictWriter(csv_string, fieldnames=keys if big_array else [])

					#writer = csv.DictWriter(csv_string, fieldnames=big_array[0].keys() if big_array else [])
					writer.writeheader()
					writer.writerows(big_array)
					return csv_string.getvalue()  

			elif len(data) == 1:
				writer = csv.DictWriter(csv_string, fieldnames=one_array.keys() if one_array else [])
				writer.writeheader()
				writer.writerows(data)
				return csv_string.getvalue()

			else:
				writer = csv.DictWriter(csv_string, fieldnames=one_array.keys() if one_array else [])
				writer.writeheader()
				writer.writerows(one_array)
				return csv_string.getvalue()

		writer = csv.DictWriter(csv_string, fieldnames=data[0].keys() if data else [])
		writer.writeheader()
		writer.writerows(data)
		return csv_string.getvalue()

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