import collections
import logging
import json
import math
from collections import deque
from node import Node
from operator import itemgetter
from h3math import Point4d, compute_radius, compute_hyperbolic_area, compute_delta_phi, compute_delta_theta

from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Circle, PathPatch
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


"""
Customized exception for invalid edge input. 
"""


class InvalidArgument(Exception):
    pass


"""
The tree structure storing all nodes and edges, and also provide easy node lookup. 
"""


class Tree(object):

    """
    This is the constructor for tree class. 

    :param int root: the root id of the tree, default None
    :param (int, int) edges: a tuple for a tree edge as (child, parent), default None
    :type nodes: set( dict( int parent, int child) ), the lookup table for the tree
    """

    def __init__(self, root=None, edges=None):
        self.nodes = {}
        self.height = 0
        self.root = root
        for e in edges:
            self.insert_edge(e[0], e[1])

    """
    Insert edge(child, parent) pair into the tree. If the parent is not given, the node is the root. 
    If the parent id is given but the child node is the root, an exception is raised for cycling 
    back to the root. If the root is set already and trying to set again, an exception is raised for
    setting a duplicate root. 

    :param int node_id: the child id
    :param int parent: the parent id
    :returns: return the Node object just been added to the tree, indicates it's added successfully
    """

    def insert_edge(self, node_id, parent=None):
        node = Node(node_id, parent)
        if parent is not None:
            if parent not in self.nodes:
                if node_id == self.root:
                    logging.error("You attempted to introduce a cycle back to the root \n")
                    raise InvalidArgument("You attempted to introduce a cycle back to the root \n")
                self.nodes[parent] = Node(node_id)
            self.nodes[parent].children.append(node_id)
            if node_id in self.nodes:
                self.nodes[node_id].parent = parent
            else:
                self.nodes[node_id] = node
        else:
            if self.root is not None:
                logging.error("You attempted to introduce a duplicate root \n")
                raise InvalidArgument("You attempted to introduce a duplicate root \n")
            self.root = node_id
            self.nodes[node_id] = node
        return node

    """
    Get all the leaf nodes in a set. 

    :param set[ dict( int child, int parent) ] edges: the edge list for all edges of the tree
    :returns: the set of all leaf nodes
    """

    def get_leaf_nodes(self, edges):
        children = set(e[0] for e in edges)
        parents = set(e[1] for e in edges)
        return children - parents

    """
    Print the tree sorted by depth to log, including the following parameters. 
    The tree is traversed in a breath-first-search. 

    :param int: the node id
    :param int parent: its parent id
    :param int depth: the depth of the node in the tree 
    :param int #children: number of children
    :param int size: the size of its subtree rooted at this node
    :param float radius: the radius of its hemisphere
    :param float area: the size of its hemispherical area
    """

    def print_tree(self):
        current_generation = deque([self.root])
        next_generation = True
        while next_generation:
            next_generation = deque()
            while current_generation:
                node_id = current_generation.popleft()
                logging.info(
                    "{0}, parent: {1}, depth: {2}, #children: {3}, size: {4}, radius: {5}, area: {6}"
                    .format(node_id,
                            self.nodes[node_id].parent,
                            self.nodes[node_id].depth,
                            len(self.nodes[node_id].children),
                            self.nodes[node_id].tree_size,
                            self.nodes[node_id].radius,
                            self.nodes[node_id].area))
                for child in self.nodes[node_id].children:
                    next_generation.append(child)
            current_generation = next_generation

    """
    Set the depth in the tree for each node. 

    :param int depth: the initial depth value for the root, default 0
    """

    def set_node_depth(self, depth=0):
        current_generation = deque([self.root])
        next_generation = True
        while next_generation:
            next_generation = deque()
            while current_generation:
                node_id = current_generation.popleft()
                self.nodes[node_id].depth = depth
                for child in self.nodes[node_id].children:
                    next_generation.append(child)
            depth += 1
            current_generation = next_generation
        self.height = depth - 1

    """
    Set the node's hemisphere radius and also its distance from its children. The radius is calculated
    recursively from the leaf nodes, with a unit hemisphere size, tracing back to the root. The area
    calculation is an approximation from a disc of the bottom of a child hemisphere to a spherical cap. 
    The recusion requires tracing the tree from the last generation to root so that all the nodes radii
    have been calculated before their parent's radius is calcualted. As the hemisphere sizes are tightly 
    calculated but placing them loosely to the parent hemisphere, the space reservation is 7.2 times of 
    the actual size of a child hemisphere. 

    :param set[ dict( int child, int parent) ] edges: the edge list for all edges of the tree
    """

    def set_subtree_radius(self, edges):
        alpha = 10.2
        leaf_nodes = self.get_leaf_nodes(edges)
        outermost_non_leaf = set()
        for n in leaf_nodes:
            N = len(self.nodes[self.nodes[n].parent].children)
            self.nodes[n].radius = compute_radius(0.0025)  # this is walrus way, H3Viewer (N / alpha)
            logging.info("leaf node {0}, parent {1}, radius {2}"
                         .format(n, self.nodes[n].parent, self.nodes[n].radius))
            outermost_non_leaf.add(self.nodes[n].parent)
        depth = self.height - 1
        current_generation = deque(list(set(n for n in outermost_non_leaf
                                            if self.nodes[n].parent is not None
                                            if self.nodes[self.nodes[n].parent].depth == depth)))
        previous_generation = True
        while previous_generation:
            previous_generation = deque()
            while current_generation:
                n = current_generation.popleft()
                if self.nodes[n].area == 0:  # avoid duplicate parents
                    if self.nodes[n].parent is not None:
                        previous_generation.append(self.nodes[n].parent)
                    for child in self.nodes[n].children:
                        self.nodes[n].area += 7.2 * compute_hyperbolic_area(self.nodes[child].radius)
                        logging.info("node {0}, child {1}, child_area+ {2}, radius {3}, area {4}"
                                     .format(n, child, compute_hyperbolic_area(self.nodes[child].radius),
                                             self.nodes[child].radius, self.nodes[child].area))
                    self.nodes[n].radius = compute_radius(self.nodes[n].area)
                    logging.info("---> node {0}, radius {1}, area {2}"
                                 .format(n, self.nodes[n].radius, self.nodes[n].area))
            for n in outermost_non_leaf:
                if n is not None:
                    if self.nodes[n].depth == depth:
                        previous_generation.append(n)
            depth -= 1
            current_generation = deque(list(set(previous_generation)))

    """
    Set the subtree size by the number of nodes in its subtree.
    :param set[ dict( int child, int parent) ] edges: the edge list for all edges of the tree
    """

    def set_subtree_size(self, edges):
        leaf_nodes = self.get_leaf_nodes(edges)
        depth = self.height
        current_generation = deque(list(n for n in leaf_nodes
                                        if self.nodes[n].depth == depth))
        previous_generation = True
        while previous_generation:
            depth -= 1
            previous_generation = deque()
            while current_generation:
                n = current_generation.popleft()
                if self.nodes[n].parent is not None:
                    previous_generation.append(self.nodes[n].parent)
                    self.nodes[self.nodes[n].parent].tree_size += \
                        self.nodes[n].tree_size
            for n in leaf_nodes:
                if self.nodes[n].depth == depth:
                    previous_generation.append(n)
            current_generation = deque(list(set(previous_generation)))

    """
    Sort the nodes in decreasing order in the same depth by their radii, in place sort is used. 
    The tree is traversed in a breath-first-search. 
    """

    def sort_children_by_radius(self):
        depth = 0
        current_generation = deque([self.root])
        next_generation = True
        while next_generation:
            next_generation = deque()
            while current_generation:
                node_id = current_generation.popleft()
                for child in self.nodes[node_id].children:
                    next_generation.append(child)
                child_size_pair = [[child, self.nodes[child].radius]
                                   for child in self.nodes[node_id].children]
                child_size_pair.sort(key=itemgetter(1), reverse=True)
                if child_size_pair:
                    self.nodes[node_id].children = list(zip(*child_size_pair)[0])
            depth += 1
            current_generation = next_generation

    """
    Sort the nodes in decreasing order in the same depth by their number of nodes in subtree, 
    in place sort is used.  This is an alternative option to sort the tree before placing the 
    nodes on the hemisphere. The original H3 algorithem set leaf node radius as math:: N / alpha
    so the nodes with many sibilings can have a larger radius and nodes with a lot of children. 
    """

    def sort_children_by_tree_size(self):
        depth = 0
        current_generation = deque([self.root])
        next_generation = True
        while next_generation:
            next_generation = deque()
            while current_generation:
                node_id = current_generation.popleft()
                for child in self.nodes[node_id].children:
                    next_generation.append(child)
                child_size_pair = [[child, self.nodes[child].tree_size]
                                   for child in self.nodes[node_id].children]
                child_size_pair.sort(key=itemgetter(1), reverse=True)
                if child_size_pair:
                    self.nodes[node_id].children = list(zip(*child_size_pair)[0])
            depth += 1
            current_generation = next_generation

    """
    Placing the hemispheres on the root hemisphere. Start from the pole, placing the largest child
    hemisphere and then placing smaller hemispheres around the pole. When the hemispheres fully filled
    one band, start placing on the next band until fully filled again. 
    Node: 
        - Placing the 1st hemisphere and its phi is zero, could lead to a ZeroDivisionError exception 
          so we set its value as a very small number (0.000001)
        - Don't forget to reserve space for the other half of the hemisphere, both the right half and 
          the lower half. Add theta by delta_theta after placing each node. Add phi by the max 
          delta_phi in the last band before placing hemispheres to the next band
        - Each subtree is independent from each other, so if the new node has a different parent node 
          than the previous parent node, we know this node is in a different subtree and initialize 
          phi, theta, dealta_theta and band and placing nodes all over again. 
    """

    def set_placement(self):
        depth = 0
        current_generation = deque(self.nodes[self.root].children)
        next_generation = True
        last_parent = self.root
        while next_generation:
            next_generation = deque()
            phi, theta, delta_theta, band = 0.000001, 0., 0., 1
            last_max_phi = 0  # span phi before jumping to the next band
            while current_generation:
                node = current_generation.popleft()
                if self.nodes[node].parent != last_parent:  # same gen, diff parent
                    last_parent = self.nodes[node].parent
                    phi, theta, delta_theta, band = 0.000001, 0., 0., 1
                rp = self.nodes[self.nodes[node].parent].radius
                try:
                    if phi == 0.000001:  # first child of root
                        phi += compute_delta_phi(self.nodes[node].radius, rp)
                        self.nodes[node].band = 0
                    else:
                        delta_theta = compute_delta_theta(self.nodes[node].radius, rp, phi)
                        if (theta + delta_theta) <= 2 * math.pi:
                            theta += delta_theta
                            if last_max_phi:
                                last_max_phi = compute_delta_phi(self.nodes[node].radius, rp)
                                phi += compute_delta_phi(self.nodes[node].radius, rp)
                        else:
                            band += 1
                            theta = delta_theta
                            phi += last_max_phi + compute_delta_phi(self.nodes[node].radius, rp)
                            last_max_phi = 0
                        self.nodes[node].band = band
                        self.nodes[node].theta = theta
                        self.nodes[node].phi = phi
                except ZeroDivisionError as e:
                    logging.error("{0}\n node {1}, radius={2}, rp={3}, phi={4}, parent={5}"
                                  .format(e, node, self.nodes[node].radius, rp, phi,
                                          self.nodes[node].parent))
                self.nodes[node].coord.sph_to_cart(self.nodes[node].theta,
                                                   self.nodes[node].phi,
                                                   self.nodes[self.nodes[node].parent].radius)
                if self.nodes[node].parent != self.root:
                    self.nodes[node].coord.coordinate_transformation(
                        self.nodes[self.nodes[node].parent].theta,
                        self.nodes[self.nodes[node].parent].phi)
                    self.nodes[node].coord.cart_offset(self.nodes[self.nodes[node].parent].coord)
                logging.info("node {0}, radius {1},  band {2}, theta {3}, phi {4}"
                             .format(node, self.nodes[node].radius, self.nodes[node].band,
                                     self.nodes[node].theta, self.nodes[node].phi))
                logging.info("node {0}, x {1}, y {2}, z {3}, w {4}"
                             .format(node, self.nodes[node].coord.x, self.nodes[node].coord.y,
                                     self.nodes[node].coord.z, self.nodes[node].coord.w))
                theta += delta_theta    # reserve space for the other half sphere
                for child in self.nodes[node].children:
                    next_generation.append(child)
            depth += 1
            current_generation = next_generation

    """
    Plot the tree with nodes and edges, optionally equators and tagging nodes with node numbers. 
    The tree is traversed in a breath-first-search. 
    Note: 
        - To distinct each generations, a color plate of ["blue", "red", "yellow", "green", "black"] 
          is used repeatedly. 
        - The X, Y, Z axises have been labelled. 
        - When the number of nodes is large and the tree is bushy, it's advised disabling tagging for
          better user experience.

    :param bool equators: whether to draw the 3D equators, default True
    :param bool tagging: whether to tag nodes with node numbers, default True
    :param int depth_cap: a filter for rendering the first N generations, default tree height
    """

    def scatter_plot(self, equators=True, tagging=True, depth_cap=None):
        if depth_cap is None:
            depth_cap = self.height
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        xs = [self.nodes[self.root].coord.x]
        ys = [self.nodes[self.root].coord.y]
        zs = [self.nodes[self.root].coord.z]
        plot_color_board = ["blue", "red", "yellow", "green", "black"]
        font0 = FontProperties()
        font0.set_size(8)
        current_generation = deque([self.root])
        next_generation = True
        while next_generation:
            next_generation = deque()
            while current_generation:
                n = current_generation.popleft()
                if self.nodes[n].depth <= depth_cap:
                    xs.append(self.nodes[n].coord.x)
                    ys.append(self.nodes[n].coord.y)
                    zs.append(self.nodes[n].coord.z)
                    if tagging:
                        ax.text(self.nodes[n].coord.x + 0.01,
                                self.nodes[n].coord.y + 0.01,
                                self.nodes[n].coord.z + 0.01,
                                ("n{0}".format(n)), fontproperties=font0)
                for child in self.nodes[n].children:
                    next_generation.append(child)
                    if self.nodes[n].depth <= depth_cap:
                        xe = [self.nodes[n].coord.x, self.nodes[child].coord.x]
                        ye = [self.nodes[n].coord.y, self.nodes[child].coord.y]
                        ze = [self.nodes[n].coord.z, self.nodes[child].coord.z]
                        ax.plot(xe, ye, ze, plot_color_board[self.nodes[n].depth % 5])
            current_generation = next_generation
        ax.scatter(xs, ys, zs, c="r", marker="o")
        global_radius = self.nodes[self.root].radius * 1.12
        if equators:
            for axis in ["x", "y", "z"]:
                circle = Circle((0, 0), global_radius * 1.1)
                circle.set_clip_box(ax.bbox)
                circle.set_edgecolor("gray")
                circle.set_alpha(0.3)
                circle.set_facecolor("none")  # "none" not None
                ax.add_patch(circle)
                art3d.pathpatch_2d_to_3d(circle, z=0, zdir=axis)
        ax.set_xlim([-1.2 * global_radius, 1.2 * global_radius])
        ax.set_ylim([-1.2 * global_radius, 1.2 * global_radius])
        ax.set_zlim([-1.2 * global_radius, 1.2 * global_radius])
        ax.set_xlabel("X Label")
        ax.set_ylabel("Y Label")
        ax.set_zlabel("Z Label")
        plt.show()

"""
A wrapper for all function calls to get the layout. 

:param (int, int) edges: a tuple for a tree edge as (child, parent), default None
:param int root: the root id of the tree, default None
:return: returns a Tree structure with layout information
"""


def get_layout(root, edges):
    tree = Tree(root, edges)
    tree.set_node_depth()
    tree.set_subtree_radius(edges)
    tree.set_subtree_size(edges)
    tree.sort_children_by_radius()
    tree.set_placement()
    return tree
