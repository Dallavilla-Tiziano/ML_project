from dataclasses import dataclass, field
import pandas as pd
import pickle
import os
import copy
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


# Class that contains data
@dataclass
class dataObj:
	''' This class is ment to store clinical and measurement data'''
	path: str
	name: str
	data: pd.DataFrame()
	type_of_data: str
	analysis: dict = field(default_factory=dict)
	description: str = ''
	is_data_index_set: bool = False

	def size(self):
		return [len(self.data.index), len(self.data.columns)]


class dataObjAnalysis:
	def __init__(self, dataManagerObj, name='DataObjAnalysis'):
		self.dataObjAnalysis_name = name
		self.parameter_container = {}
		self.setDataManagerObj(dataManagerObj)
		self.initializeParameterContainer()

	def initializeParameterContainer(self):
		self.parameter_container['StandardScaler'] = {}

	def updateParameterContainer(self, function_name, parameter_dict):
		self.parameter_container[function_name] = parameter_dict

	def setDataManagerObj(self, dataManagerObj):
		'''Assign a dataManager object to the class for further analysis'''
		if isinstance(dataManagerObj, dataManager):
			self.dataManager = dataManagerObj
		else:
			raise ValueError(f''''{name}' is not a valid dataManager object!''')

	def computePCA(self, dataObj_name, **kwargs):
		'''Standardize features and perform PCA'''
		dataObj = self.dataManager.getDataObj(dataObj_name)
		kwargs_ss = self.parameter_container['StandardScaler']
		standard_scaler = StandardScaler(**kwargs_ss)




class dataManager:
	def __init__(self, name='dataManager'):
		self.data_container = {}
		self.dataManager_name = name

	def createDataObject(self, path, name, type_of_data, description='', sep=',', data=None, index_col=None):
		'''Create a dataObj and store it in data_container'''
		if (type_of_data != 'measurement') and (type_of_data != 'clinical') and (type_of_data != 'accessory'):
			raise ValueError('Type can only be \'measurement\' or \'clinical\'')
		elif name in self.data_container:
			raise ValueError(f'''A data object named '{name}' is already present in the /
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

	def getDataObj(self, name):
		if name in self.data_container:
			return copy.deepcopy(self.data_container[name])
		else:
			raise KeyError(f'No data object named {name} is present in the data container!')

	def setDataObjIndex(self, name, index_col):
		dataObj = self.getDataObj(name)
		if dataObj.data.index.name == index_col:
			print(f'{index_col} is already set as index for {name} data object.')
		elif index_col in dataObj.data.columns:
			dataObj.data.set_index(index_col, inplace=True)
			indexed = not isinstance(dataObj.data.index, pd.RangeIndex)
			dataObj.is_data_index_set = indexed
			self.data_container[name] = dataObj
		else:
			raise ValueError(f'{index_col} is not in {dataObj.name} columns')

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
			dataObj = self.getDataObj(key)
			print(f'Name: {key}')
			if extended:
				print(f'Path: {dataObj.path}')
				print(f'Type of data: {dataObj.type_of_data}')
				print(f'Rows: {dataObj.size()[0]}')
				print(f'Columns: {dataObj.size()[1]}')
				print(f'Description: {dataObj.description}')
				print(f'Is indexed: {dataObj.is_data_index_set}')
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

# IS THE FOLLOWING FUNCTION USEFUL????
	def dataObjectJoin(self, dataObj1_name, dataObj2_name, name='', del_parents=False, **kwargs):
		'''Perform a join operation on 2 dataObj'''
		dataObj1 = self.getDataObj(dataObj1_name)
		dataObj2 = self.getDataObj(dataObj2_name)
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

	def joinIndexes(self, dataObj1_name, dataObj2_name, del_parents=False):
		'''Intersect two dataObj and create two new tables with containing only /
		common elements by index'''
		dataObj1 = self.getDataObj(dataObj1_name)
		dataObj2 = self.getDataObj(dataObj2_name)
		if dataObj1.is_data_index_set and dataObj2.is_data_index_set:
			common_indexes = list(set(dataObj1.data.index).intersection(dataObj2.data.index))
			dataObj1.data = dataObj1.data.loc[common_indexes]
			dataObj2.data = dataObj2.data.loc[common_indexes]
			newdataObj1_name = f'{dataObj1.name}.joinIndexes({dataObj2.name})'
			newdataObj2_name = f'{dataObj2.name}.joinIndexes({dataObj1.name})'
			newdataObj1_type_of_data = dataObj1.type_of_data
			newdataObj2_type_of_data = dataObj2.type_of_data
			newdataObj_description = f'''result of joinIndexes between {dataObj1.name} and {dataObj2.name}'''
			self.createDataObject('', newdataObj1_name, newdataObj1_type_of_data, newdataObj_description, data=dataObj1.data)
			self.createDataObject('', newdataObj2_name, newdataObj2_type_of_data, newdataObj_description, data=dataObj2.data)
			if del_parents:
				self.deleteDataObject(dataObj1.name, dataObj2.name)
		else:
			print('''Your dataset doesn\'t have an index, or is index if of type /
					pd.RangeIndex. Please note that this type of index is not supported /
					during operation such as join. Please set a different type of index /
					with \'setDataObjIndex\'''')
