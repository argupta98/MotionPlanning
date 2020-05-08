"""A Class holding all the relevant classes for point location."""

import numpy as np
from sortedcontainers import SortedDict

class Trapezoid(object):
    """Represents a single Trapezoid."""

    def __init__(self, vertices, originator_vertices, parent=None):
        self.vertices = vertices
        # find two topmost point
        y_sorted = np.argsort(self.vertices[:, 1])
        self.top_line = make_lr(self.vertices[y_sorted[2:]])
        self.bottom_line = make_lr(self.vertices[y_sorted[:2]])
        self.left_p = self.vertices[np.argmin(self.vertices[:, 0])]
        self.right_p = self.vertices[np.argmax(self.vertices[:, 0])]
        assert(self.left_p[0] < self.right_p[0]), "left p: {} right_p: {}  all points: {}".format(self.left_p, self.right_p, self.vertices)
        self.parent = parent
        self.originators = originator_vertices
        self.index = 0 

    def __repr__(self):
        return "Trapezoid: {}".format(self.index)

    def set_idx(self, i):
        self.index = i
    
    def set_parent(self, parent):
        self.parent = parent

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
        assert(edge[0, 0] < edge[1, 0])
        # Cannot have an intersection
        # Check edge below the top line
        if edge[0, 0] < self.top_line[0, 0]:
            criteria_top = linear_interpolation(edge, self.top_line[0, 0]) <= self.top_line[0, 1]
            criteria_bottom = linear_interpolation(edge, self.bottom_line[0, 0]) >= self.bottom_line[0, 1]

        else: 
            criteria_top = edge[0, 1] <= linear_interpolation(self.top_line, edge[0, 0])
            criteria_bottom = edge[0, 1] >= linear_interpolation(self.bottom_line, edge[0, 0])

        if not criteria_top:
            print("[Trapezoid {}] top hight criteria not met".format(self.index))
            return False
        
        if not criteria_bottom:
            print("[Trapezoid {}] bottom hight criteria not met".format(self.index))
            return False
        
        if edge[1][0] <= self.left_p[0]:
            print("[Trapezoid {}] edge <= left_pt".format(self.index))
            return False
        
        if edge[0][0] >= self.right_p[0]:
            print("[Trapezoid {}] edge >= right_pt".format(self.index))
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

    def split_by(self, edge):
        """ Returns the trapezoids formed as a result of splitting by an edge. 
            `top`: 
            `left`:
            `right`:
            `bottom`:
        """
        new_traps = {}
        curr_trap = self

        if curr_trap.is_intersected(edge):
            print("\n[Trapezoid {}] Splitting".format(self.index))
            assert(edge[0, 0] < edge[1, 0])
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
            # TODO Shorten the appropriate extensions and merge appropriate trapezoids

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

    def right_adjacent(self, index):
        trap = self.trapezoids[index]
        if trap.rightp()[0] in self.by_left_x:
            choices = self.by_left_x[trap.rightp()[0]]
        else:
            return []
        # First line under the top line
        idx = choices.bisect_left(trap.top()[1, 1])
        keys = choices.keys()
        if idx < len(keys) and idx >= 0:
            curr_trap = choices[keys[idx]]
        else:
            return []

        print("right adjacent keys: {}".format(keys))
        right_adjacent = []
        while trap.top()[1, 1] > curr_trap.bottom()[0, 1]:
            if trap.bottom()[1, 1] < curr_trap.top()[0, 1]:
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
        self.by_left_x[trap.leftp()[0]].pop(trap.top()[0, 1])

    def clean(self):
        # TODO: Reset indices in the trapezoids
        # self.to_remove.sort(key=lambda x:-x)
        # for idx in self.to_remove:
        #    self.trapezoids.remove(idx)
        pass

    def add(self, trapezoid):
        self.trapezoids.append(trapezoid)

        if trapezoid.leftp()[0] not in self.by_left_x:
            self.by_left_x[trapezoid.leftp()[0]] = SortedDict()
        self.by_left_x[trapezoid.leftp()[0]].update([(trapezoid.top()[0, 1], trapezoid)])

        # if trapezoid.rightp()[0] not in self.by_right_x:
        #     self.by_right_x[trapezoid.rightp()[0]] = SortedDict()
        #self.by_right_x[trapezoid.rightp()[0]].update((trapezoid.top()[1, 1], trapezoid))
        trapezoid.set_idx(len(self.trapezoids) - 1)
        return trapezoid.index
        
    def to_graph(self):
        """Turns the trapezoids into a searchable graph."""
        pass


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


class PointQuery(Query):
    def __call__(self, point):
        if point[0] <= self.x:
            return self.true_child
        return self.false_child

def linear_interpolation(edge, x):
    m = float(edge[0][1] - edge[1][1]) / float(edge[0][0] - edge[1][0])
    if m != 0:
        b = edge[0][1] - m * edge[0][0]
        return m * x + b
    else:
        assert(edge[0][1] == edge[1][1])
        return edge[0][1]

def make_lr(edge):
    left_idx = np.argmin(edge[:, 0])
    return np.array([edge[left_idx], edge[1 - left_idx]])

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
        start_trap.set_parent(self.tree_root)

    def lines(self):
        """ Returns a list of all the lines in the point locator object for easy visualization."""
        traps = self.trapezoids.trap_list()
        lines = []
        for trapezoid in traps:
            for idx in range(len(trapezoid)):
                lines.append(np.array([trapezoid[idx], trapezoid[(idx + 1) % len(trapezoid)]]))
        return lines

    def add_line(self, edge):
        """ Add a line segment defined by p1 and p2 to the point location struct."""
        edge = make_lr(edge)
        p_l = edge[0]
        p_r = edge[1]

        # 1) Find the trapezoids that are intersected by the segment
        left_trap = self.query(p_l)
        right_trap = self.query(p_r)
        intersected_traps = [left_trap]

        if left_trap != right_trap:
            # Iterate through left trapezoids until find the trapezoid with p_r in it
            intersected = True
            while intersected:
                print("edge while")
                traps = self.trapezoids.right_adjacent(left_trap)
                print("left_trap: {}".format(left_trap))
                print("traps: {}".format(traps))
                if right_trap in traps or len(traps) == 0:
                    break
                
                intersected = False
                for trap_idx in traps:
                    if self.trapezoids[trap_idx].is_intersected(edge):
                        intersected_traps.append(trap_idx)
                        left_trap = trap_idx
                        intersected = True
                        break
            intersected_traps.append(right_trap)

        print("intersected_traps: {}".format(intersected_traps))
        # 2) Make the new trapezoids formed by the addition of the segment
        new_traps = []
        for trap_idx in intersected_traps:
            new_traps.append(self.trapezoids[trap_idx].split_by(edge))

        for i, trap_idx in enumerate(intersected_traps):
            # 4) Remove the leaves of the tree corresponding to the old trapezoid + remove from trapezoids
            if len(new_traps[i]) > 0:
                parent = self.pop_leaf(trap_idx)
                to_add = new_traps[i] 

                indices = {}
                for key, trap in to_add.items():
                    indices[key] = self.trapezoids.add(trap)

                if "top" in indices:
                    # 5) Replace them with the appropriate query into the new leaves
                    new_node = SegmentQuery(edge, indices["top"], indices["bottom"])
                    self.trapezoids[indices["top"]].set_parent(new_node)
                    self.trapezoids[indices["bottom"]].set_parent(new_node)
                else:
                    assert(len(indices) == 0)
                    continue

                if "right" in indices:
                    new_node = PointQuery(p_r[0], new_node, indices["right"])
                    self.trapezoids[indices["right"]].set_parent(new_node)
                
                if "left" in indices:
                    new_node = PointQuery(p_l[0], indices["left"], new_node)
                    self.trapezoids[indices["left"]].set_parent(new_node)

                parent.set_value(new_node)

        self.trapezoids.clean()


    def pop_leaf(self, idx):
        parent = self.trapezoids[idx].parent
        self.trapezoids.pop(idx)
        if parent.true_child == idx:
            parent.true_child = None
        elif parent.false_child == idx:
            parent.false_child = None
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
                raise ValueError("[PointLocator] got null end node!")
                return None