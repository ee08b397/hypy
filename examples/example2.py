import igraph
from h3.tree import Tree, get_layout

"""
An example for drawing a random spanning tree with 500 nodes without tagging or equators.
"""
if __name__ == '__main__':
    edges = igraph.Graph.Barabasi(n=500, m=3, directed=True).spanning_tree(None, True).get_edgelist()
    tree = get_layout(0, edges)
    tree.scatter_plot(equators=False, tagging=False)
