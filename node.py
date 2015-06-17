import collections
import json

class Node:
	def __init__(self, nodeId):
		self.__nodeId = nodeId
		self.__children = [] 

	@property
	def nodeId(self):
		return self.__nodeId

	@property
	def children(self):
		return self.__children
	
	def insert_child(self, nodeId):
		self.__children.append(nodeId)	

