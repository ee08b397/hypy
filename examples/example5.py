import igraph
import collections
import logging
import json
import csv
from collections import deque

from hypy.tree import Tree

"""
Export layout to csv: x, y, z
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
    return get_coordinates(tree)

def get_coordinates(tree):
    coord_list = []
    current_generation = deque([tree.root])
    next_generation = True
    while next_generation:
        next_generation = deque()
        while current_generation:
            node_id = current_generation.popleft()
            coord_list.append([tree.nodes[node_id].coord.x,
                               tree.nodes[node_id].coord.y,
                               tree.nodes[node_id].coord.z])
            coord_list.append([tree.nodes[node_id].coord.x,
                               tree.nodes[node_id].coord.y,
                               tree.nodes[node_id].coord.z])
            for child in tree.nodes[node_id].children:
                next_generation.append(child)
        current_generation = next_generation
    return coord_list

if __name__ == '__main__':
    result = []
    with open('coordinates.csv', 'w') as fp:
        csv_w = csv.writer(fp, delimiter=',')
        csv_w.writerows([['x', 'y', 'z', 'lp_x', 'lp_y', 'lp_z', 'hp_x', 'hp_y', 'hp_z']])
        csv_w.writerows(calc_layout(10**3))
    fp.close
