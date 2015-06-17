import igraph
import collections
import json

def bas():
	g = igraph.Graph.Barabasi(n=10, m=2)
	return g.spanning_tree(None, True).get_edgelist()

#http://xahlee.info/perl-python/python_construct_tree_from_edge.html
def construct_tree(edges, root):
	"""Given a list of edges [child, parent], return trees. """
	trees = collections.defaultdict(dict)

	for parent,child in edges:
			trees[parent][child] = trees[child]

	children, parents = zip(*edges)
	return {root: trees[root]}

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

class Tree:
	def __init__(self):
		self.__nodes = {}
		
	@property
	def nodes(self):
		return self.__nodes
		
	def insert_node(self, nodeId, parent = None):	 
		node = Node(nodeId)
		self[nodeId] = node

		if parent is not None:
			self[parent].insert_child(nodeId)

		return node
	
	def printTree(self, nodeId, depth = 0):
		children = self[nodeId].children
		if depth == 0:
			print ("{0}".format(nodeId))
		else:
			print "\t" * depth, "{0}".format(nodeId)

		depth += 1
		for child in children:
			self.printTree(child, depth)		

	def __getitem__(self, key):
		return self.__nodes[key]

	def __setitem__(self, key, item):
		self.__nodes[key] = item



if __name__ == '__main__':
	# edges = [[0, 2], [3, 0], [1, 4], [2, 4], [5, 6], [6, 7], [8, 6]]
	edges = bas()
	print edges	
	tree = construct_tree(edges, 0)
	print(json.dumps(tree, indent=2))
	
	tree = Tree()
	tree.insert_node(0)
	for e in edges:
		tree.insert_node(e[1], e[0])
	
	tree.printTree(0)
