import collections
import json

class Node:
	def __init__(self, nodeId, parentId = None):
		self.__nodeId = nodeId
		self.__children = [] 
		self.__parent = parentId

	@property
	def parent(self):
		return self.__parent
		
	@property
	def nodeId(self):
		return self.__nodeId

	@property
	def children(self):
		return self.__children
	
	def insert_child(self, nodeId):
		self.__children.append(nodeId)	

