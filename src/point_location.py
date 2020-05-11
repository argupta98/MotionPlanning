"""A Class holding all the relevant classes for point location."""

import numpy as np
from sortedcontainers import SortedDict
from .line_utils import *

class Trapezoid(object):
    """Represents a single Trapezoid."""

    def __init__(self, vertices, originator_vertices):
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
        return "Trapezoid: {} - {}".format(self.index, self.vertices)

    def set_idx(self, i):
        self.index = i
    
    def add_parent(self, parent):
        if isinstance(parent, list):
            self.parents.extend(parent)
        else:
            self.parents.append(parent)

    def set_line(self, top=True):
        """ Processes vertices to get the correct top line. """
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
        # Cannot have an intersection
        # Check edge below the top line (left side)
        if edge[0, 0] < self.top_line[0, 0]:
            criteria_top_left = linear_interpolation(edge, self.top_line[0, 0]) <= self.top_line[0, 1] + 10**-6
            criteria_bottom_left = linear_interpolation(edge, self.bottom_line[0, 0]) >= self.bottom_line[0, 1] - 10 **-6

        else: 
            criteria_top_left = edge[0, 1] <= linear_interpolation(self.top_line, edge[0, 0]) + 10**-6
            criteria_bottom_left = edge[0, 1] >= linear_interpolation(self.bottom_line, edge[0, 0]) - 10**-6

        if not criteria_top_left:
            # print("\n[Trapezoid {}] top hight left criteria not met\n Edge: {} \nVertices: {}\n------------\n".format(self.index, edge, self.vertices))
            return False
        
        if not criteria_bottom_left:
            # print("\n[Trapezoid {}] bottom hight left criteria not met\n Edge: {} \nVertices: {}\n------------\n".format(self.index, edge, self.vertices))
            return False

        # check below top line (right side)
        if edge[1, 0] > self.top_line[1, 0]:
            criteria_top_right = linear_interpolation(edge, self.top_line[1, 0]) <= self.top_line[1, 1] + 10**-6
            criteria_bottom_right = linear_interpolation(edge, self.bottom_line[1, 0]) >= self.bottom_line[1, 1] - 10**-6

        else: 
            criteria_top_right = edge[1, 1] <= linear_interpolation(self.top_line, edge[1, 0]) + 10**-6
            criteria_bottom_right = edge[1, 1] >= linear_interpolation(self.bottom_line, edge[1, 0]) - 10**-6
            # print("edge[1, 1]: {} >= linear_interpolation: {}: {}".format(edge[1, 1], linear_interpolation(self.bottom_line, edge[1, 0]), criteria_bottom_right))

        if not criteria_top_right:
            # print("\n[Trapezoid {}] top hight right criteria not met\n Edge: {} \nVertices: {}\n------------\n".format(self.index, edge, self.vertices))
            return False
        
        if not criteria_bottom_right:
            # print("\n[Trapezoid {}] bottom hight right criteria not met\n Edge: {} \nVertices: {}\n------------\n".format(self.index, edge, self.vertices))
            return False
        
        if edge[1][0] <= self.left_p[0]:
            # print("\n[Trapezoid {}] edge right x < left_p \n Edge: {} \nVertices: {}\n------------\n".format(self.index, edge, self.vertices))
            return False
        
        if edge[0][0] >= self.right_p[0]:
            # print("\n[Trapezoid {}] edge left x > right_p\n Edge: {} \nVertices: {}\n------------\n".format(self.index, edge, self.vertices))
            return False
        return True

    def includes_point_loose(self, point):
        """Returns if the point is inside the trapezoid."""
        if point[0] < self.left_p[0] or point[0] > self.right_p[0]:
            return False

        y_upper = linear_interpolation(self.top_line, point[0])
        y_lower = linear_interpolation(self.bottom_line, point[0])

        if point[1] < y_lower - 10**-6 or point[1] > y_upper + 10**-6:
            return False
        return True

    def includes_point(self, point):
        """Returns if the point is inside the trapezoid."""
        if point[0] <= self.left_p[0] or point[0] >= self.right_p[0]:
            return False

        y_upper = linear_interpolation(self.top_line, point[0])
        y_lower = linear_interpolation(self.bottom_line, point[0])

        if point[1] <= y_lower or point[1] >= y_upper:
            return False
        return True
    
    def raw(self):
        return self.vertices

    def is_left_pointed(self):
        top_y = self.top_line[0, 1]
        bottom_y = self.bottom_line[0, 1]
        return top_y == bottom_y

    def is_right_pointed(self):
        top_y = self.top_line[1, 1]
        bottom_y = self.bottom_line[1, 1]
        return top_y == bottom_y

    def split_by(self, edge):
        """ Returns the trapezoids formed as a result of splitting by an edge. 
            `top`: 
            `left`:
            `right`:
            `bottom`:
            `merge left`:
            `merge right`:
        """
        new_traps = {}
        merge = {}
        curr_trap = self

        if curr_trap.is_intersected(edge):
            # print("\n[Trapezoid {}] Splitting".format(self.index))
            assert(edge[0, 0] <= edge[1, 0])
            # Check for endpoints within trapezoid
            for i, key in enumerate(["left", "right"]):
                # print(key)
                # print("curr_trap points: {}".format(curr_trap.raw()))
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

                    # Update which things originated the appropriate lines
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

                    # print("leftover_points: {}".format(leftover_points))
                    # Make the remaining trapezoid:
                    curr_trap = Trapezoid(leftover_points, leftover_originators)

            # Ensure nothing went wrong an the edge intersects the trapezoid
            # assert(curr_trap.is_intersected(edge))

            # Split the remaining trapezoid area into top and bottom

            if edge[0, 0] < edge[1, 0]:
                # Center line for split
                center_left = [curr_trap.left_p[0], linear_interpolation(edge, curr_trap.left_p[0])]
                center_right = [curr_trap.right_p[0], linear_interpolation(edge, curr_trap.right_p[0])]
                center_points = np.array([center_right, center_left])

                # print("center: {}".format(center_points))
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

            else:
                assert("right" not in new_traps)
                if "left" in new_traps:
                    new_traps["right"] = curr_trap

            # Shorten the appropriate extensions and merge appropriate trapezoids
            # for originator in curr_trap.originators:
            #    top_originator_points = np.argwhere(top_points[:, 0] == originator[0])[:, 0]
            #    if originator[1] < 
        return new_traps


class Trapezoids(object):
    """A class to hold a list of joint trapezoids"""
    def __init__(self):
        # Keep trapezoids by their left x_coordinate and right x_coordinate
        self.trapezoids = []
        self.to_remove = []
        # For finding right adjacent
        self.by_left_x = {}

        # self.by_right_x = {}

    def trap_list(self):
        """Returns all the trapezoids in point form."""
        traps = []
        for trapezoid in self.trapezoids:
            if trapezoid is not None:
                traps.append(trapezoid.raw())
        return traps

    def trap_count(self):
        count = 0
        for trap in self.trapezoids:
            if trap is not None:
                # print(trap)
                count += 1
        return count

    def right_adjacent_to(self, x):
        if x in self.by_left_x:
            # print("[Right-Adjacent-To] x: {} values: {}".format(x, self.by_left_x[x]))
            return self.by_left_x[x]
        return []

    def right_adjacent(self, index):
        """Returns all trapezoids that share the right edge with the current 
        one.
        """
        trap = self.trapezoids[index]
        if trap.rightp()[0] in self.by_left_x:
            choices = self.by_left_x[trap.rightp()[0]]
        else:
            return []
        # First bottom line below the top line
        idx = choices.bisect_left(trap.top()[1, 1])
        # print("trap top: {}".format(trap.top()[1, 1]))
        if idx == len(choices):
           idx -= 1

        # print(idx)
        keys = choices.keys()
        # print("[Right-adjacent] keys: {}".format(keys))
        if idx >= 0:
            curr_trap = choices[keys[idx]]
        else:
            return []

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
        trap = self.trapezoids[idx]
        self.trapezoids[idx] = None
        self.to_remove.append(idx)
        if trap is not None and not trap.is_left_pointed():
            self.by_left_x[trap.leftp()[0]].pop(trap.bottom()[0, 1])

    def clean(self):
        # TODO: Reset indices in the trapezoids
        # self.to_remove.sort(key=lambda x:-x)
        # for idx in self.to_remove:
        #    self.trapezoids.remove(idx)
        pass
    
    
    def add(self, trapezoid):
        assert(trapezoid is not None)
        self.trapezoids.append(trapezoid)

        if not trapezoid.is_left_pointed(): # Don't insert triangles that will never be intersected
            x = trapezoid.left_p[0]
            if x not in self.by_left_x:
                self.by_left_x[x] = SortedDict()
            self.by_left_x[x].update([(trapezoid.bottom()[0, 1], trapezoid)])

        trapezoid.set_idx(len(self.trapezoids) - 1)
        return trapezoid.index
    
    def update_idx(self, idx, trapezoid):
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
        new_trapezoids = []
        for trap_idx in indices:
            trap = self.trapezoids[trap_idx]
            split_traps = trap.split_by(edge)
            new_trapezoids.append(split_traps)
        return new_trapezoids
    
    def add_and_check_merges(self, trapezoids):
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
        # Check same originator vertex for line
        if (trap_left.originators[-1] != trap_right.originators[0]).any():
            # print("[Trapezoids] Merge failed at originator check")
            return None

        # Check vertices to merge are the same
        left_merger = np.array([trap_left.top_line[1], trap_left.bottom_line[1]])
        right_merger = np.array([trap_right.top_line[0], trap_right.bottom_line[0]])
        if not np.allclose(left_merger, right_merger, atol=10**-1):
            # print("[Trapezoids] Merge failed at same vertices check: \n {} \n\n{}".format(left_merger, right_merger))
            return None

        # Check that the slopes match
        left_top_slope = slope(trap_left.top())
        right_top_slope = slope(trap_right.top())
        left_bottom_slope = slope(trap_left.bottom())
        right_bottom_slope = slope(trap_right.bottom())
        if not np.allclose(left_top_slope, right_top_slope) or \
           not np.allclose(left_bottom_slope, right_bottom_slope):
           # print("[Trapezoids] Merge Failed at slope check")
           return None

        # Check both vertices either above or below the originator 
        # print("Originator: {}".format(trap_left.originators[-1]))
        if (left_merger[:, 1] <= trap_left.originators[-1, 1]).all() or \
           (left_merger[:, 1] >= trap_left.originators[-1, 1]).all():
            # print("[Trapezoids] Merge Succeeed!!")
            new_trap_verts = [trap_left.top_line[0], trap_right.top_line[1]]
            if not np.allclose(trap_right.bottom_line[1], trap_right.top_line[1]):
                new_trap_verts.append(trap_right.bottom_line[1])

            if not np.allclose(trap_left.bottom_line[0], trap_left.top_line[0]):
                new_trap_verts.append(trap_left.bottom_line[0])
            new_trap_verts = np.array(new_trap_verts)
            new_trap_originators = np.concatenate([trap_left.originators[:-1], trap_right.originators[1:]])
            return Trapezoid(new_trap_verts, new_trap_originators)

        # print("[Trapezoids] Merge failed both above, below check.")
        return None



class Query(object):
    def __init__(self, x, true_child, false_child):
        self.x = x
        self.true_child = true_child
        self.false_child = false_child
    
    def set_value(self, node):
        if self.true_child is None:
            self.true_child = node
        elif self.false_child is None:
            self.false_child = node
        else:
            raise ValueError("[Query] Neither child is none!")
    
    def unfilled(self):
        return self.true_child is None or self.false_child is None


class PointQuery(Query):
    def __call__(self, point):
        if point[0] <= self.x:
            return self.true_child
        return self.false_child


class SegmentQuery(Query):
    def __call__(self, point):
        y = linear_interpolation(self.x, point[0])
        if point[1] > y:
            return self.true_child
        return self.false_child

class PointLocator(object):
    """ A point location datastructure that can be queried to find the appropriate polygon. """
    
    def __init__(self, bounds):
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
        return self.trapezoids.trap_list()

    def remove_traps_within_polygons(self, polygons):
        self.trapezoids.remove_traps_within_polygons(polygons)

    def add_line(self, edge):
        """ Add a line segment defined by p1 and p2 to the point location struct."""
        edge = make_lr(edge)
        p_l = edge[0]
        p_r = edge[1]

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
                # print("traps: {}".format(traps))
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
            # print("Intersected: {}".format(intersected_traps))
            assert(last_includes_point), "Last point Not included in last Trapezoid!! Are there intersecting Polygons?"
            # intersected_traps.append(right_trap)


        # 2) Make the new trapezoids formed by the addition of the segment
        new_traps = self.trapezoids.split_trapezoids(edge, intersected_traps)

        parents = []
        for i, trap_idx in enumerate(intersected_traps):
            if len(new_traps[i]) > 0:
                parents.append(self.pop_leaf(trap_idx))
            else:
                parents.append(None)

        new_traps = self.trapezoids.add_and_check_merges(new_traps)                

        for i, trap_idx in enumerate(intersected_traps):
            # 4) Remove the leaves of the tree corresponding to the old trapezoid + remove from trapezoids
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

        self.trapezoids.clean()


    def pop_leaf(self, idx):
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