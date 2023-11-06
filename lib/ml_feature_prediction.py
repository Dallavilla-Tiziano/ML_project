from dataclasses import dataclass
import pandas as pd


# Class that contains data
@dataclass
class dataObj:
	path: str
	data: pd.DataFrame()
	type_of_data: str


class dataManager:
	def createDataObject(path, type_of_data, sep=','):
		if type not in ['measurement', 'clinical']:
			print('Type can only be \'measurement\' or \'clinical\'')
		else:
			data = pd.read_csv(path, sep=sep)
		return dataObj(path, data, type_of_data)