import igraph
import collections
import logging
import json
import csv
from timeit import Timer

from hypy.tree import Tree

"""
Benchmark the performance of getting layout
"""


def calc_layout(num_nodes):
    edges = igraph.Graph.Barabasi(n=num_nodes, m=3, directed=True).\
        spanning_tree(None, True).get_edgelist()
    tree = Tree(0, edges)
    tree.set_node_depth()
    tree.set_subtree_radius(edges)
    tree.set_subtree_size(edges)
    tree.sort_children_by_radius()
    tree.set_placement()

if __name__ == '__main__':
    result = []
    print("#nodes\t\ttime")
    for num_nodes in [10, 10 ** 2, 10 ** 3, 10 ** 4, 10 ** 5]:
        t = Timer(lambda: calc_layout(num_nodes))
        lapse = t.timeit(number=10) / 10.0
        result.append((num_nodes, lapse))
        print("{0}\t\t{1}".format(num_nodes, lapse))
    with open('result.csv', 'w') as fp:
        csv_w = csv.writer(fp, delimiter=',')
        csv_w.writerows([['#nodes', 'time']])
        csv_w.writerows(result)
    fp.close()
