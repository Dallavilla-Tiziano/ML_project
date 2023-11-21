from dataclasses import dataclass, field
import pandas as pd
import pickle
import os
import copy
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import numpy as np


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
		self.parameter_container['StandardScaler.fit_transform'] = {}
		self.parameter_container['PCA'] = {}
		self.parameter_container['PCA.fit_transform'] = {}

	def updateParameterContainer(self, function_name, parameter_dict):
		'''Update a set of parameter for a function with a new set'''
		self.parameter_container[function_name] = parameter_dict

	def setDataManagerObj(self, dataManagerObj):
		'''Assign a dataManager object to the class for further analysis'''
		if isinstance(dataManagerObj, dataManager):
			self.dataManager = dataManagerObj
		else:
			raise ValueError('The variable specified is not a valid dataManager object')

	def updateDataObjectAnalysis(self, a_dataObj, analysis_name, result):
		'''Add a result to a dataObj analysis dict'''
		a_dataObj.analysis[analysis_name] = result
		self.dataManager.updateDataObject(a_dataObj)

	def computePCA(self, dataObj_name, **kwargs):
		'''Standardize features and perform PCA'''
		dataObj = self.dataManager.getDataObj(dataObj_name)

		kwargs_ss = self.parameter_container['StandardScaler']
		standard_scaler = StandardScaler(**kwargs_ss)
		kwargs_ssf = self.parameter_container['StandardScaler.fit_transform']
		df_scaled = pd.DataFrame(standard_scaler.fit_transform(dataObj.data, **kwargs_ssf), columns=dataObj.data.columns, index=dataObj.data.index,)
		self.updateDataObjectAnalysis(dataObj, 'StandardScaler', standard_scaler)
		self.updateDataObjectAnalysis(dataObj, 'StandardScaler.fit_transform', df_scaled)

		kwargs_pca = self.parameter_container['PCA']
		pca = PCA(**kwargs_pca)
		kwargs_ssf = self.parameter_container['PCA.fit_transform']
		df_pca = pd.DataFrame(pca.fit_transform(df_scaled), index=df_scaled.index)
		df_pca.columns = ['PC' + str(i) for i in range(1, len(df_pca.columns) + 1)]
		self.updateDataObjectAnalysis(dataObj, 'PCA', pca)
		self.updateDataObjectAnalysis(dataObj, 'PCA.fit_transform', df_pca)

### IS THE FOLLOWING FUNCTION USEFUL?
	def plotPCA(self, m_dataOBj_name, c_dataObj_name='', target='', pcs=['PC1', 'PC2', 'PC3']):
		'''Plot PCA and optionally visualize groups based on target column of clinical_dataObj)'''
		width = 1000
		height = 1000

		m_dataObj = self.dataManager.getDataObj(m_dataOBj_name)
		pc_df = m_dataObj.analysis['PCA.fit_transform']
		pc_df.sort_index(inplace=True)
		if c_dataObj_name and target:
			c_dataObj = self.dataManager.getDataObj(c_dataObj_name)
			target_df = c_dataObj.data[[target]]
			target_df.sort_index(inplace=True)
			if pc_df.index.equals(target_df.index):
				fig = px.scatter_3d(
					pc_df,
					x=pcs[0],
					y=pcs[1],
					z=pcs[2],
					color=target_df[target],
					width=width,
					height=height)
		else:
			fig = px.scatter_3d(
				pc_df,
				x=pcs[0],
				y=pcs[1],
				z=pcs[2],
				width=width,
				height=height)
		fig.update_traces(marker_size=3)
		fig.show()

	def plotComponentsMatrix(self, m_dataOBj_name, c_dataObj_name='', target='', components):
		m_dataObj = self.dataManager.getDataObj(m_dataOBj_name)
		if c_dataObj_name and target:
			c_dataObj = self.dataManager.getDataObj(c_dataObj_name)
			col = c_dataObj.data[target]
		else:
			col = 'k'
		# check if components is a list of strings
		if bool(lst) and not isinstance(lst, basestring) and all(isinstance(elem, basestring) for elem in lst):
			features = components
		# check if components is a list of int
		elif bool(lst) and not isinstance(lst, basestring) and all(isinstance(elem, int) for elem in lst):
			features = m_dataObj.analysis['PCA.fit_transform'].columns[components]
		else:
			features = m_dataObj.analysis['PCA.fit_transform'].columns[list(range(0:6))]

		fig = px.scatter_matrix(
			m_dataObj.analysis['PCA.fit_transform'],
			dimensions=features,
			color=col,
			height=1000,
			opacity=0.5
		)
		fig.update_traces(diagonal_visible=False)
		fig.show()

	def getCentroidCoordinates(self, m_dataOBj_name, c_dataObj_name, target):
		m_dataObj = self.dataManager.getDataObj(m_dataOBj_name)
		c_dataObj = self.dataManager.getDataObj(c_dataObj_name)
		m_dataObj.analysis['PCA.fit_transform']['grouping'] = list(c_dataObj.data[target])
		pca_groups = m_dataObj.analysis['PCA.fit_transform'].groupby('grouping')
		centroids_coordinates = {}
		for index, group in pca_groups:
			centroid = np.array(group.iloc[:, 0:-1].mean())
			centroids_coordinates[index] = centroid
		centroids_coordinates_df = pd.DataFrame(centroids_coordinates).T
		centroids_coordinates_df.columns = ['PC' + str(i) for i in range(1, len(centroids_coordinates_df.columns) + 1)]
		self.updateDataObjectAnalysis(m_dataObj, 'getCentroidCoordinates', centroids_coordinates_df)




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
			self.data_container[name] = dataObj(path, name, data, type_of_data, description=description, is_data_index_set=indexed)
		elif not (path) and (data is not None):
			indexed = not isinstance(data.index, pd.RangeIndex)
			self.data_container[name] = dataObj(path, name, data, type_of_data, description=description, is_data_index_set=indexed)
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

	def updateDataObject(self, new_dataObj):
		if new_dataObj.name in self.data_container:
			self.data_container[new_dataObj.name] = new_dataObj
		else:
			raise KeyError(f'No data object named {new_dataObj.name} is present in the data container!')

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
			self.createDataObject('', newdataObj1_name, newdataObj1_type_of_data, description=newdataObj_description, data=dataObj1.data)
			self.createDataObject('', newdataObj2_name, newdataObj2_type_of_data, description=newdataObj_description, data=dataObj2.data)
			if del_parents:
				self.deleteDataObject(dataObj1.name, dataObj2.name)
		else:
			print('''Your dataset doesn\'t have an index, or is index if of type /
					pd.RangeIndex. Please note that this type of index is not supported /
					during operation such as join. Please set a different type of index /
					with \'setDataObjIndex\'''')