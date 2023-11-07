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

	def createDataObject(self, path, name, type_of_data, description='', sep=',', data=None):
		'''Create a dataObj and store it in data_container'''
		if (type_of_data != 'measurement') and (type_of_data != 'clinical') and (type_of_data != 'accessory'):
			raise ValueError('Type can only be \'measurement\' or \'clinical\'')
		elif (path) and (data is None):
			data = pd.read_csv(path, sep=sep)
			self.data_container[name] = dataObj(path, name, data, type_of_data, description)
		elif not (path) and (data is not None):
			self.data_container[name] = dataObj(path, name, data, type_of_data, description)
		else:
			print('''something went wrong while creating a data object, \
					it is not possible to continue. Please check you parameters \
					and ensure they are correct.''')

	def deleteDataObject(self, *args):
		'''Delete a dataObj from data_container'''
		for name in args:
			try:
				self.data_container.pop(name)
			except KeyError:
				print(f'No data object named {name} is present in the data container!')
				continue

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

	def dataObjectJoin(self, dataObj1, dataObj2, del_parents=False, **kwargs):
		'''Perform a join operation on 2 dataObj'''
		data = dataObj1.join(dataObj2, kwargs)
		name = f'joined {dataObj1.name} and {dataObj2.name}'
		type_of_data = dataObj1.type_of_data
		description = f'''results of join between {dataObj1.name} and /
		{dataObj2.name} with the following parameters: {kwargs}'''
		self.createDataObject('', name, type_of_data, description, data=data)
		if del_parents:
			self.deleteDataObject(dataObj1.name, dataObj2.name)

