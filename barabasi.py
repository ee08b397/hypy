import igraph

def bas():
	g = igraph.Graph.Barabasi(n=10, m=2)
	# g.spanning_tree(None, True).get_edgelist()
	# print g.get_edgelist()
	# return g.get_edgelist()
	return g.spanning_tree(None, True).get_edgelist()

# bas()

import collections
import json
#http://xahlee.info/perl-python/python_construct_tree_from_edge.html

def construct_trees(edges):
	"""Given a list of edges [child, parent], return trees. """
	trees = collections.defaultdict(dict)

	for child, parent in edges:
			trees[parent][child] = trees[child]

	# Find roots
	children, parents = zip(*edges)
	roots = set(parents).difference(children)

	return {root: trees[root] for root in roots}

if __name__ == '__main__':
	# edges = [[0, 2], [3, 0], [1, 4], [2, 4], [5, 6], [6, 7], [8, 6]]
	edges = bas()
	print(json.dumps(construct_trees(edges), indent=2))
	graph = construct_trees(edges)
	print graph



