from dataclasses import dataclass
import pandas as pd


# Class that contains data
@dataclass
class dataObj:
	''' This class is ment to store clinical and measurement data'''
	path: str
	name: str
	data: pd.DataFrame()
	type_of_data: str
	description: str = ''


class dataManager:
	def __init__(self):
		self.data_container = {}

	def createDataObject(self, path, name, type_of_data, description='', sep=','):
		'''Create a dataObj and store it in data_container'''
		if (type_of_data != 'measurement') and (type_of_data != 'clinical') and (type_of_data != 'accessory'):
			raise ValueError('Type can only be \'measurement\' or \'clinical\'')
		else:
			data = pd.read_csv(path, sep=sep)
			self.data_container[name] = dataObj(path, name, data, type_of_data, description)

	def deleteDataObject(self, name):
		'''Delete a dataObj from data_conteiner'''
		self.data_container.pop(name, f'No data object named {name} is present in the data container!')

	def printDataContainer(self, extended=False):
		'''Print the dataObj names present in data_container, if extended = True 
		also print path, type_of_data, and decription'''
		for key in self.data_container:
			print(f'Name: {key}')
			if extended:
				print(f'Path: {self.data_container[key].path}')
				print(f'Type of data: {self.data_container[key].type_of_data}')
				print(f'Description: {self.data_container[key].description}')
			print('---END---')