"""Classes to hold useful functions on trapezoids."""

import numpy as np
from sortedcontainers import SortedDict
from .line_utils import *


class Trapezoid(object):
    """Represents a single Trapezoid."""

    def __init__(self, vertices, originator_vertices=None):
        """
        Args:
            vertices (np.ndarray): An (n, 2) array of 2d vertex coordinates.
            originator_vertices (list): the vertices that originated the left and right lines, if applicable.
        """
        self.vertices = vertices
        # find two topmost point
        y_sorted = np.argsort(self.vertices[:, 1])
        idx = 2
        if len(vertices) == 3:
            idx = 1
        self.top_line = self.set_line(top=True)
        self.bottom_line = self.set_line(top=False)
        self.left_p = self.vertices[np.argmin(self.vertices[:, 0])]
        self.right_p = self.vertices[np.argmax(self.vertices[:, 0])]
        assert(self.left_p[0] < self.right_p[0]), "left p: {} right_p: {}  all points: {}".format(self.left_p, self.right_p, self.vertices)
        self.parents = []

        # Can have at most 2 originators
        assert(len(originator_vertices) <= 2)
        self.originators = []
        if len(originator_vertices) > 0:
            self.originators = make_lr(np.array(originator_vertices))
        self.index = 0 

    def __repr__(self):
        """String representation for printing."""
        return "Trapezoid: {} - {}".format(self.index, self.vertices)

    def set_idx(self, i):
        """Set the index field."""
        self.index = i
    
    def add_parent(self, parent):
        """Appends all the parents in parent to self.parents."""
        if isinstance(parent, list):
            self.parents.extend(parent)
        else:
            self.parents.append(parent)

    def set_line(self, top=True):
        """ Processes vertices to get the correct top line / bottom line."""
        y_sorted = np.argsort(self.vertices[:, 1])
        idx = 0
        if top:
            idx = -1
        start = self.vertices[y_sorted[idx]]
        left_idx = (y_sorted[idx] - 1) % len(self.vertices)
        right_idx = (y_sorted[idx] + 1) % len(self.vertices)
        contenders = np.array([self.vertices[left_idx], self.vertices[right_idx]])
        diffs = contenders - start
        if (diffs[:, 0] == 0).any():
            end = contenders[np.argwhere(diffs[:, 0] != 0)[0, 0]]
        else:
            if top:
                end = contenders[np.argmax(contenders[:, 1])]
            else:
                end = contenders[np.argmin(contenders[:, 1])]
        return make_lr(np.array([start, end]))

    def top(self):
        """Returns the top-most segment of the trapezoid."""
        return self.top_line

    def bottom(self):
        """Returns the bottom-most segment of the trapezoid."""
        return self.bottom_line

    def leftp(self):
        """Returns the left-most point of the trapezoid."""
        return self.left_p

    def rightp(self):
        """Returns the right-most point of the trapezoid."""
        return self.right_p
    
    def is_intersected(self, edge):
        """ Returns whether an edge intersects the trapezoid."""
        assert(edge[0, 0] <= edge[1, 0])
        # Check edge below the top line (left side)
        if edge[0, 0] < self.top_line[0, 0]:
            criteria_top_left = linear_interpolation(edge, self.top_line[0, 0]) <= self.top_line[0, 1] + 10**-6
            criteria_bottom_left = linear_interpolation(edge, self.bottom_line[0, 0]) >= self.bottom_line[0, 1] - 10 **-6

        else: 
            criteria_top_left = edge[0, 1] <= linear_interpolation(self.top_line, edge[0, 0]) + 10**-6
            criteria_bottom_left = edge[0, 1] >= linear_interpolation(self.bottom_line, edge[0, 0]) - 10**-6

        if not criteria_top_left or not criteria_bottom_left:
            return False
        
        # check below top line (right side)
        if edge[1, 0] > self.top_line[1, 0]:
            criteria_top_right = linear_interpolation(edge, self.top_line[1, 0]) <= self.top_line[1, 1] + 10**-6
            criteria_bottom_right = linear_interpolation(edge, self.bottom_line[1, 0]) >= self.bottom_line[1, 1] - 10**-6

        else: 
            criteria_top_right = edge[1, 1] <= linear_interpolation(self.top_line, edge[1, 0]) + 10**-6
            criteria_bottom_right = edge[1, 1] >= linear_interpolation(self.bottom_line, edge[1, 0]) - 10**-6

        if not criteria_top_right or not criteria_bottom_right:
            return False

        # check left and right edges 
        if edge[1][0] <= self.left_p[0]:
            return False
        
        if edge[0][0] >= self.right_p[0]:
            return False
        return True

    def includes_point_loose(self, point):
        """Returns if the point is inside the trapezoid or on edges."""
        if point[0] < self.left_p[0] or point[0] > self.right_p[0]:
            return False

        y_upper = linear_interpolation(self.top_line, point[0])
        y_lower = linear_interpolation(self.bottom_line, point[0])

        if point[1] < y_lower - 10**-6 or point[1] > y_upper + 10**-6:
            return False
        return True

    def includes_point(self, point):
        """Returns if the point is strictly inside the trapezoid."""
        if point[0] <= self.left_p[0] or point[0] >= self.right_p[0]:
            return False

        y_upper = linear_interpolation(self.top_line, point[0])
        y_lower = linear_interpolation(self.bottom_line, point[0])

        if point[1] <= y_lower or point[1] >= y_upper:
            return False
        return True
    
    def raw(self):
        """Returns the raw vertices of the trapezoid."""
        return self.vertices

    def is_left_pointed(self):
        """Returns whether the trapezoid converges to a point on the left side."""
        top_y = self.top_line[0, 1]
        bottom_y = self.bottom_line[0, 1]
        return top_y == bottom_y

    def is_right_pointed(self):
        """Returns whether the trapezoid converges to a point on the right side."""
        top_y = self.top_line[1, 1]
        bottom_y = self.bottom_line[1, 1]
        return top_y == bottom_y

    def split_by(self, edge):
        """ Returns the trapezoids formed as a result of splitting by an edge. 
            `top`: trapezoid on top
            `left`: trapezoid on left
            `right`: trapezoid on right
            `bottom`: trapezoid on bottom
        """
        new_traps = {}
        merge = {}
        curr_trap = self

        if curr_trap.is_intersected(edge):
            assert(edge[0, 0] <= edge[1, 0])
            for i, key in enumerate(["left", "right"]):
                if curr_trap.includes_point(edge[i]):
                    # Top and bottom of the line from the line endpoint
                    top_point = [edge[i][0], linear_interpolation(curr_trap.top_line, edge[i][0])]
                    bottom_point = [edge[i][0], linear_interpolation(curr_trap.bottom_line, edge[i][0])]
                    center_points = [top_point, bottom_point]

                    points = [curr_trap.bottom_line[i]]
                    if curr_trap.top_line[i][1] !=  curr_trap.bottom_line[i][1]:
                        points.append(curr_trap.top_line[i])

                    points = np.array(center_points + points)

                    leftover_points = [curr_trap.bottom_line[1 - i]]
                    if curr_trap.top_line[1 - i][1] !=  curr_trap.bottom_line[1 - i][1]:
                        leftover_points.append(curr_trap.top_line[1 - i])

                    leftover_points = np.array(center_points + leftover_points)

                    # Update which points originated the appropriate lines
                    new_originators = []
                    leftover_originators = []
                    for originator in curr_trap.originators:
                        if originator[0] in points[:, 0]:
                            new_originators.append(originator)
                        if originator[0] in leftover_points[:, 0]:
                            leftover_originators.append(originator)
                    new_originators.append(edge[i])
                    leftover_originators.append(edge[i])

                    trap = Trapezoid(points, new_originators)
                    new_traps[key] = trap

                    # Make the remaining trapezoid:
                    curr_trap = Trapezoid(leftover_points, leftover_originators)

            # Split the remaining trapezoid area into top and bottom
            if edge[0, 0] < edge[1, 0]:
                # Center line for split
                center_left = [curr_trap.left_p[0], linear_interpolation(edge, curr_trap.left_p[0])]
                center_right = [curr_trap.right_p[0], linear_interpolation(edge, curr_trap.right_p[0])]
                center_points = np.array([center_right, center_left])

                # Top and bottom trapezoid points
                top_points = np.concatenate([center_points, curr_trap.top()], axis=0)
                bottom_points = np.concatenate([center_points, curr_trap.bottom()], axis=0)

                top_originators = []
                bottom_originators = []
                for originator in curr_trap.originators:
                    if originator[0] in top_points[:, 0]:
                        top_originators.append(originator)
                    if originator[0] in bottom_points[:, 0]:
                        bottom_originators.append(originator)

                new_traps["top"] = Trapezoid(top_points, top_originators)
                new_traps["bottom"] = Trapezoid(bottom_points, bottom_originators)

            else: # case of vertical edge, split into left and right
                assert("right" not in new_traps)
                if "left" in new_traps:
                    new_traps["right"] = curr_trap

        return new_traps


class Trapezoids(object):
    """A class to hold a list of joint trapezoids"""
    def __init__(self):
        self.trapezoids = []
        self.to_remove = []
        # For finding right adjacent
        self.by_left_x = {}

    def trap_list(self):
        """Returns all the trapezoids in point form."""
        traps = []
        for trapezoid in self.trapezoids:
            if trapezoid is not None:
                traps.append(trapezoid.raw())
        return traps

    def trap_count(self):
        """Return the number of trapezoids in the list."""
        count = 0
        for trap in self.trapezoids:
            if trap is not None:
                count += 1
        return count

    def right_adjacent_to(self, x):
        """Return the dictionary of all trapezoids right of the provided x coordinate."""
        if x in self.by_left_x:
            return self.by_left_x[x]
        return {}

    def right_adjacent(self, index):
        """Returns all trapezoids that share the right edge with the trapezoid at index.
        """
        trap = self.trapezoids[index]
        if trap.rightp()[0] in self.by_left_x:
            choices = self.by_left_x[trap.rightp()[0]]
        else:
            return []
        # First bottom line below the top line
        idx = choices.bisect_left(trap.top()[1, 1])
        if idx == len(choices):
           idx -= 1

        keys = choices.keys()
        if idx >= 0:
            curr_trap = choices[keys[idx]]
        else:
            return []

        # Find adjacent
        right_adjacent = []
        while trap.bottom()[1, 1] <= curr_trap.top()[0, 1]:
            if trap.top()[1, 1] >= curr_trap.bottom()[0, 1]:
                right_adjacent.append(curr_trap.index)
            
            idx -= 1
            if idx >= 0:
                curr_trap = choices[keys[idx]]
            else:
                break
        return right_adjacent

    def __getitem__(self, idx):
        return self.trapezoids[idx]
    
    def pop(self, idx):
        """Remove the trapezoid at index."""
        trap = self.trapezoids[idx]
        self.trapezoids[idx] = None
        self.to_remove.append(idx)
        if trap is not None and not trap.is_left_pointed():
            self.by_left_x[trap.leftp()[0]].pop(trap.bottom()[0, 1])
    
    def add(self, trapezoid):
        """Add a trapezoid to the set."""
        assert(trapezoid is not None)
        if len(self.to_remove) > 0:
            idx = self.to_remove[-1]
            self.to_remove.pop(-1)
            self.trapezoids[idx] = trapezoid
        else:
            self.trapezoids.append(trapezoid)
            idx = len(self.trapezoids) - 1

        if not trapezoid.is_left_pointed(): # Don't insert triangles that will never be intersected
            x = trapezoid.left_p[0]
            if x not in self.by_left_x:
                self.by_left_x[x] = SortedDict()
            self.by_left_x[x].update([(trapezoid.bottom()[0, 1], trapezoid)])

        trapezoid.set_idx(idx)
        return trapezoid.index
    
    def update_idx(self, idx, trapezoid):
        """Exchange the trapezoid at the given index for a new one."""
        assert(trapezoid is not None)
        old_trap = self.trapezoids[idx] 
        if not old_trap.is_left_pointed():
            self.by_left_x[old_trap.leftp()[0]].pop(old_trap.bottom()[0, 1])

        self.trapezoids[idx] = trapezoid
        if not trapezoid.is_left_pointed():
            trapezoid.set_idx(idx)
            x = trapezoid.leftp()[0]
            if x not in self.by_left_x:
                self.by_left_x[x] = SortedDict()
            self.by_left_x[x].update([(trapezoid.bottom()[0, 1], trapezoid)])

    def remove_traps_within_polygons(self, polygons):
        """ Removes trapezoids that lie within a polygon in polygons. """
        for trap in self.trapezoids:
            if trap is not None and polygons.contains_trap(trap):
                self.pop(trap.index)
    
    def split_trapezoids(self, edge, indices):
        """Split trapezoids at indices by the edge."""
        new_trapezoids = []
        for trap_idx in indices:
            trap = self.trapezoids[trap_idx]
            split_traps = trap.split_by(edge)
            new_trapezoids.append(split_traps)
        return new_trapezoids
    
    def add_and_check_merges(self, trapezoids):
        """Add the trapezoids and merge the relevant ones."""
        for i in range(len(trapezoids)):
            split_traps = trapezoids[i]
            for key, trap in split_traps.items():
                split_traps[key] = self.add(trap)

            if i > 0:
                last_splits = trapezoids[i-1]
                for key in ["top", "bottom"]:
                    if key in last_splits and key in split_traps:
                        merged_trap = self.try_merge(self.trapezoids[last_splits[key]],
                                                     self.trapezoids[split_traps[key]])
                        if merged_trap is not None:
                            self.pop(split_traps[key])
                            split_traps[key] = last_splits[key]
                            self.update_idx(last_splits[key], merged_trap)
                        
                        assert(self.trapezoids[last_splits[key]] is not None)
                        assert(self.trapezoids[split_traps[key]] is not None)
        return trapezoids
    
    def try_merge(self, trap_left, trap_right):
        """Try to merge two trapezoids."""
        # Check same originator vertex for line
        if (trap_left.originators[-1] != trap_right.originators[0]).any():
            return None

        # Check vertices to merge are the same
        left_merger = np.array([trap_left.top_line[1], trap_left.bottom_line[1]])
        right_merger = np.array([trap_right.top_line[0], trap_right.bottom_line[0]])
        if not np.allclose(left_merger, right_merger, atol=10**-1):
            return None

        # Check that the slopes match
        left_top_slope = slope(trap_left.top())
        right_top_slope = slope(trap_right.top())
        left_bottom_slope = slope(trap_left.bottom())
        right_bottom_slope = slope(trap_right.bottom())
        if not np.allclose(left_top_slope, right_top_slope) or \
           not np.allclose(left_bottom_slope, right_bottom_slope):
           return None

        # Check both vertices either above or below the originator 
        if (left_merger[:, 1] <= trap_left.originators[-1, 1]).all() or \
           (left_merger[:, 1] >= trap_left.originators[-1, 1]).all():
            new_trap_verts = [trap_left.top_line[0], trap_right.top_line[1]]
            if not np.allclose(trap_right.bottom_line[1], trap_right.top_line[1]):
                new_trap_verts.append(trap_right.bottom_line[1])

            if not np.allclose(trap_left.bottom_line[0], trap_left.top_line[0]):
                new_trap_verts.append(trap_left.bottom_line[0])
            new_trap_verts = np.array(new_trap_verts)
            new_trap_originators = np.concatenate([trap_left.originators[:-1], trap_right.originators[1:]])
            return Trapezoid(new_trap_verts, new_trap_originators)

        return None
