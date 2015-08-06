import igraph
import collections
import logging
import json

from h3.tree import Tree

"""
An example for drawing a random spanning tree with 500 nodes without tagging or equators.
"""
if __name__ == '__main__':
    edges = igraph.Graph.Barabasi(n=500, m=3, directed=True).spanning_tree(None, True).get_edgelist()
    logging.info(edges)
    tree = Tree(0, edges)
    tree.set_node_depth()
    tree.set_subtree_radius(edges)
    tree.set_subtree_size(edges)
    tree.sort_children_by_radius()  # alternatively, tree.sort_children_by_tree_size()
    tree.set_placement()
    tree.scatter_plot(equators=False, tagging=False)
