import igraph
import collections
import json

from barabasi import bas
from tree import Tree
from tree import construct_tree 

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
