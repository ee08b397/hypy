import igraph

def bas():
	g = igraph.Graph.Barabasi(n=10, m=2)
	return g.spanning_tree(None, True).get_edgelist()
