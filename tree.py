import collections
import json

from node import Node 

#http://xahlee.info/perl-python/python_construct_tree_from_edge.html
def construct_tree(edges, root):
	"""Given a list of edges [child, parent], return trees. """
	trees = collections.defaultdict(dict)

	for parent,child in edges:
			trees[parent][child] = trees[child]

	children, parents = zip(*edges)
	return {root: trees[root]}



class Tree:
	def __init__(self):
		self.__nodes = {}
		
	@property
	def nodes(self):
		return self.__nodes
		

	def insert_node(self, nodeId, parent = None):	 
		node = Node(nodeId, parent)
		self[nodeId] = node

		if parent is not None:
			self[parent].insert_child(nodeId)

		return node
	

	def printTree(self, nodeId, depth = 0):
		children = self[nodeId].children
		if depth == 0:
			print ("{0}".format(nodeId))
		else:
			#print "\t" * depth, "{0}".format(nodeId)
			print "\t" * depth, "{0}, parent: {1}".format(nodeId, self[nodeId].parent)

		depth += 1
		for child in children:
			self.printTree(child, depth)		

	def __getitem__(self, key):
		return self.__nodes[key]

	def __setitem__(self, key, item):
		self.__nodes[key] = item
