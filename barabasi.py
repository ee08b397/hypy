import igraph

def bas():
	g = igraph.Graph.Barabasi(n=10, m=2)
	print g.get_edgelist()
	

bas()


