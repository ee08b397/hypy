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

if __name__ == '__main__':
	# edges = [[0, 2], [3, 0], [1, 4], [2, 4], [5, 6], [6, 7], [8, 6]]
	edges = bas()
	print edges	
	graph = construct_tree(edges, 0)
	print(json.dumps(graph, indent=2))



