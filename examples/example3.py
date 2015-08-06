import unittest
import igraph
import collections
import json

from h3.tree import Tree

"""
Customized print tree to terminal
Note: implemented by recursion, not scalable to a large number of nodes, 
      only suitable for a small number of nodes
"""


def printTree(tree, nodeId, depth=0):
    children = tree.nodes[nodeId].children
    total_children_area = 0
    for child in children:
        total_children_area += tree.nodes[child].area
    print "\t" * tree.nodes[nodeId].depth, \
        "{0}, radius: {1}, parent: {2}, area: {3}, total_children_area: {4}" \
        .format(nodeId,
                tree.nodes[nodeId].radius,
                tree.nodes[nodeId].parent,
                tree.nodes[nodeId].area,
                total_children_area)
    for child in children:
        printTree(tree, child, depth)

if __name__ == '__main__':
    edges_r = igraph.Graph.Tree(40, 3).get_edgelist()
    edges = []
    for e in edges_r:
        edges.append((e[1], e[0]))
    print edges
    tree = Tree(0, edges)
    tree.set_node_depth()
    tree.set_subtree_radius(edges)
    printTree(tree, 0)
    tree.sort_children_by_radius()
    tree.set_placement()
    tree.scatter_plot()
