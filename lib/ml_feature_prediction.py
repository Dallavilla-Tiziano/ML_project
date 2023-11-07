from dataclasses import dataclass
import pandas as pd
import pickle
import os


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
	def __init__(self, name='dataManager'):
		self.data_container = {}
		self.dataManager_name = name

	def createDataObject(self, path, name, type_of_data, description='', sep=','):
		'''Create a dataObj and store it in data_container'''
		if (type_of_data != 'measurement') and (type_of_data != 'clinical') and (type_of_data != 'accessory'):
			raise ValueError('Type can only be \'measurement\' or \'clinical\'')
		else:
			data = pd.read_csv(path, sep=sep)
			self.data_container[name] = dataObj(path, name, data, type_of_data, description)

	def deleteDataObject(self, name):
		'''Delete a dataObj from data_conteiner'''
		try:
			self.data_container.pop(name)
		except KeyError:
			print(f'No data object named {name} is present in the data container!')

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

	def saveDataManager(self, folderpath):
		'''Save the current dataManager object to the specified path'''
		filename = self.dataManager_name + '.obj'
		filepath = '/'.join([folderpath.rstrip('/'), filename])
		if os.path.isdir(folderpath):  # Check if folder exist
			if not os.path.isfile(filepath):  # Check if file already exist
				with open(filepath, 'wb') as file:
					pickle.dump(self, file)
					print(f'{self.dataManager_name} successfully saved to \'{filepath}\'')
			else:
				print(f'A file named {filename} already exist, saving process is aborted.')
		else:
			print('The path specified does not exist, saving process is aborted.')

	@classmethod
	def loadDataManager(cls, filepath):
		'''Load a dataManager objectfrom the specified path'''
		if os.path.isfile(filepath):  # Check if file exist
			with open(filepath, 'rb') as file:
				return pickle.load(file)
		else:
			print('Can\'t import the data manager object, file does not exist.')
