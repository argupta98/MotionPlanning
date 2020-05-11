"""A Class holding all the relevant classes for point location."""

import numpy as np
from sortedcontainers import SortedDict
from .line_utils import *
from trapezoids import * 

class Query(object):
    """ Base class for point location query nodes."""
    def __init__(self, x, true_child, false_child):
        """
        Args:
            x: the node differentiator
            true_child: the node to go to if evaluated as true
            false_child: the node to go to if evaluated as false.
        """
        self.x = x
        self.true_child = true_child
        self.false_child = false_child
    
    def __call__(self, point):
        raise NotImplementedError("[Query] __call__ must be implemented in child class.")
    
    def set_value(self, node):
        """Set the value of the `None` child to the node."""
        if self.true_child is None:
            self.true_child = node
        elif self.false_child is None:
            self.false_child = node
        else:
            raise ValueError("[Query] Neither child is none!")
    
    def unfilled(self):
        """Returns true if a chid is None."""
        return self.true_child is None or self.false_child is None


class PointQuery(Query):
    """ A point query object, differentiates between left and right."""
    def __call__(self, point):
        if point[0] <= self.x:
            return self.true_child
        return self.false_child

class SegmentQuery(Query):
    """ A segment query object, differentiates between top and bottom."""
    def __call__(self, point):
        y = linear_interpolation(self.x, point[0])
        if point[1] > y:
            return self.true_child
        return self.false_child

class PointLocator(object):
    """ A point location datastructure that can be queried to find the appropriate trapezoid. """
    
    def __init__(self, bounds):
        """
        Args:
            bounds: (x_min, y_min, x_max, y_max) the bounds in which the polygons reside.
        """
        self.trapezoids = Trapezoids()
        min_x, min_y, max_x, max_y = bounds
        bounds_vertices = np.array([[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y]])
        start_trap = Trapezoid(bounds_vertices, [])
        start_idx = self.trapezoids.add(start_trap)
        # Start query is the left bound
        self.tree_root = PointQuery(bounds[0], "failure", start_idx)
        start_trap.add_parent(self.tree_root)
        # For Debugging
        self.edge_history = []
        self.bounds = bounds

    def lines(self):
        """ Returns a list of all the lines in the point locator object for easy visualization."""
        traps = self.trapezoids.trap_list()
        lines = []
        for trapezoid in traps:
            for idx in range(len(trapezoid)):
                lines.append(np.array([trapezoid[idx], trapezoid[(idx + 1) % len(trapezoid)]]))
        return lines

    def traps(self):
        """ Returns a list of trapezoids that are in the data structure."""
        return self.trapezoids.trap_list()

    def remove_traps_within_polygons(self, polygons):
        """ Remove the trapezoids that lie entirely in one of the polygons."""
        self.trapezoids.remove_traps_within_polygons(polygons)

    def add_line(self, edge):
        """ Add a line segment defined by p1 and p2 to the point location struct."""
        edge = make_lr(edge)
        p_l = edge[0]
        p_r = edge[1]

        is_intersecting = False
        self.edge_history.append(edge)

        # 1) Find the trapezoids that are intersected by the segment
        left_trap = self.query(p_l)
        right_trap = self.query(p_r)
        intersected_traps = [left_trap]

        if left_trap != right_trap:
            # Iterate through left trapezoids until find the trapezoid with p_r in it
            intersected = True
            last_includes_point =  False
            while intersected:
                traps = self.trapezoids.right_adjacent(left_trap)
                intersected = False
                for trap_idx in traps:
                    if self.trapezoids[trap_idx].is_intersected(edge):
                        intersected_traps.append(trap_idx)
                        left_trap = trap_idx
                        intersected = True
                        break

                if self.trapezoids[intersected_traps[-1]].includes_point_loose(p_r):
                    last_includes_point =  True
                    break
            is_intersecting = not last_includes_point

        # 2) Make the new trapezoids formed by the addition of the segment
        new_traps = self.trapezoids.split_trapezoids(edge, intersected_traps)

        parents = []
        for i, trap_idx in enumerate(intersected_traps):
            if len(new_traps[i]) > 0:
                parents.append(self.pop_leaf(trap_idx))
            else:
                parents.append(None)

        new_traps = self.trapezoids.add_and_check_merges(new_traps)                

        # 3) Remove parents and add in in the child trapezoids from the splits
        for i, trap_idx in enumerate(intersected_traps):
            if parents[i] is not None:
                parent = parents[i]
                indices = new_traps[i] 

                if edge[0, 0] < edge[1, 0]:
                    new_node = SegmentQuery(edge, indices["top"], indices["bottom"])
                    self.trapezoids[indices["top"]].add_parent(new_node)
                    self.trapezoids[indices["bottom"]].add_parent(new_node)

                    if "right" in indices:
                        new_node = PointQuery(p_r[0], new_node, indices["right"])
                        self.trapezoids[indices["right"]].add_parent(new_node)
                    
                    if "left" in indices:
                        new_node = PointQuery(p_l[0], indices["left"], new_node)
                        self.trapezoids[indices["left"]].add_parent(new_node)
                else:
                    new_node = PointQuery(edge[0, 0], indices["left"], indices["right"])
                    self.trapezoids[indices["left"]].add_parent(new_node)
                    self.trapezoids[indices["right"]].add_parent(new_node)

                for p in parent:
                    p.set_value(new_node)

        return is_intersecting

    def pop_leaf(self, idx):
        """Remove a trapezoid from the datastructure and return its parent nodes."""
        parent = self.trapezoids[idx].parents
        self.trapezoids.pop(idx)
        for p in parent:
            if p.true_child == idx:
                p.true_child = None
            elif p.false_child == idx:
                p.false_child = None
            else:
                raise ValueError("[PointLocator] Parent does not have child: {}".format(idx))
        return parent

    def query(self, p):
        """ Queries for the point p in self. Returns the index of the trapezoid containing p."""
        curr_node = self.tree_root
        while True:
            curr_node = curr_node(p)
            if isinstance(curr_node, int):
                return curr_node
            elif curr_node is None:
                raise ValueError("[PointLocator] No trapezoid in that Area!")
                return None
            elif isinstance(curr_node, str):
                raise ValueError("[PointLocator] Obstacles out of bounds!")