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
	is_data_index_set: bool = False

	def size(self):
		return [len(self.data.index), len(self.data.columns)]


class dataManager:
	def __init__(self, name='dataManager'):
		self.data_container = {}
		self.dataManager_name = name

	def createDataObject(self, path, name, type_of_data, description='', sep=',', data=None, index_col=None):
		'''Create a dataObj and store it in data_container'''
		if (type_of_data != 'measurement') and (type_of_data != 'clinical') and (type_of_data != 'accessory'):
			raise ValueError('Type can only be \'measurement\' or \'clinical\'')
		elif name in self.data_container:
			raise ValueError(f'''A data object named {name} is already present in the /
			data manager, please choose a different name.''')
		elif (path) and (data is None):
			data = pd.read_csv(path, sep=sep, index_col=index_col)
			indexed = not isinstance(data.index, pd.RangeIndex)
			self.data_container[name] = dataObj(path, name, data, type_of_data, description, is_data_index_set=indexed)
		elif not (path) and (data is not None):
			indexed = not isinstance(data.index, pd.RangeIndex)
			self.data_container[name] = dataObj(path, name, data, type_of_data, description, is_data_index_set=indexed)
		else:
			print('''something went wrong while creating a data object, \
					it is not possible to continue. Please check you parameters \
					and ensure they are correct.''')
		if not indexed:
			print(f'''Your dataset \'{name}\' doesn\'t have an index, or is index if of type /
					pd.RangeIndex. Please note that this type of index is not supported /
					during operations such as join. Please set a different type of index /
					with \'setDataObjIndex\'''')

	def setDataObjIndex(self, name, index_col):
		if self.data_container[name].data.index.name == index_col:
			print(f'{index_col} is already set as index for {name} data object.')
		elif index_col in self.data_container[name].data.columns:
			self.data_container[name].data.set_index(index_col, inplace=True)
			indexed = not isinstance(self.data_container[name].data.index, pd.RangeIndex)
			self.data_container[name].is_data_index_set = indexed
		else:
			raise ValueError(f'{index_col} is not in {self.data_container[name].name} columns')

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
				print(f'Rows: {self.data_container[key].size()[0]}')
				print(f'Columns: {self.data_container[key].size()[1]}')
				print(f'Description: {self.data_container[key].description}')
				print(f'Is indexed: {self.data_container[key].is_data_index_set}')
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

	def dataObjectJoin(self, dataObj1_name, dataObj2_name, name='', del_parents=False, **kwargs):
		'''Perform a join operation on 2 dataObj'''
		dataObj1 = self.data_container[dataObj1_name]
		dataObj2 = self.data_container[dataObj2_name]
		if dataObj1.is_data_index_set and dataObj2.is_data_index_set:
			data = dataObj1.data.join(dataObj2.data, **kwargs)
			if not name:
				name = f'joined {dataObj1.name} and {dataObj2.name}'
			type_of_data = dataObj1.type_of_data
			description = f'''results of join between {dataObj1.name} and /
			{dataObj2.name} with the following non-default parameters: {kwargs}'''
			self.createDataObject('', name, type_of_data, description, data=data)
			if del_parents:
				self.deleteDataObject(dataObj1.name, dataObj2.name)
		else:
			print('''Your dataset doesn\'t have an index, or is index if of type /
					pd.RangeIndex. Please note that this type of index is not supported /
					during operation such as join. Please set a different type of index /
					with \'setDataObjIndex\'''')
