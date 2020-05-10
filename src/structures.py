"""Contains the classes for working with the polygons and the trapezoids in a coherent way."""

import numpy as np
import random
from matplotlib.path import Path
import math
from scipy.spatial import ConvexHull
from line_utils import *

class Polygon(object):
    """ Holds points and implements useful features."""
    def __init__(self, points):
        self.points = points
        self.edges = self._edges()
        self.center = np.mean(points, axis=0)

    def is_counterclockwise(self):
        edge_diff_1 = self.edges[0, 1] - self.edges[0, 0]
        edge_diff_2 = self.edges[1, 1] - self.edges[1, 0]
        edge_idx = 1
        z = np.cross(edge_diff_1, edge_diff_2)
        while z == 0:
            edge_diff_1 = self.edges[i, 1] - self.edges[i, 0]
            edge_diff_2 = self.edges[i+1, 1] - self.edges[i+1, 0]
            edge_idx += 1
            z = np.cross(edge_diff_1, edge_diff_2)

        return z < 0

    def counterclockwise(self):
        """Make edges go counter-clockwise."""
        # Flip if clockwise
        if not self.is_counterclockwise():
            self.points = np.flip(self.points, axis=0)
            self.edges = self._edges()

    def _edges(self):
        edges = []
        for i in range(len(self.points)):
            edges.append(np.array([self.points[i], self.points[(i+1) % len(self.points)]]))
        return np.array(edges)

    def edge_angles(self):
        """Returns edge vectors in order of angle from y axis, starting with the closest to 0."""
        edges = self.edges
        angles = []
        pos_y = np.array([0, 1])
        min_angle_idx = 0
        min_angle = 400
        for i, edge in enumerate(edges):
            # Get the normal vector that points out of the shape
            normal_vec = normal(edge)
            normal_options = np.array([normal_vec, -1 * normal_vec])
            center_line = edge.mean(axis=0) - self.center
            products = np.matmul(normal_options.T, center_line)
            normal_vec = normal_options[np.argmax(products)]
            normal_vec = np.divide(normal_vec, np.linalg.norm(normal_vec))

            # compute the angle with positive y
            # ax*by-ay*bx, ax*bx+ay*by
            tan_1 = normal_vec[0] * pos_y[1] 
            tan_2 = normal_vec[1] * pos_y[1]
            angle = math.atan2(tan_1, tan_2)
            if angle < 0:
                angle += 2 * np.pi
            angles.append(angle)
            if angle < min_angle:
                min_angle = angle
                min_angle_idx = i
        return np.array(angles), min_angle_idx

    
    def start_point(self):
        """The first point for the ordered edges."""
        pass



class Polygons(object):
    """ A class to hold several polygons and implements useful polygon operations."""

    def __init__(self, polygons):
        """
        Args:
            polygons (list): a list of (P,2) np.ndarrays which represent individual polygons.
        """
        self.polygons = polygons

    @staticmethod
    def make_convex(max_num_vertices, bounds):
        """Returns a single convex polygon with at most max_num_vertices."""
        assert(max_num_vertices >= 3)

        # Fill with the remaining vertices
        vertices = np.random.rand(max_num_vertices, 2)
        vertices[:, 0] *= bounds[1, 0] - bounds[0, 0] - 4
        vertices[:, 0] += bounds[0, 0] + 2 
        vertices[:, 1] *= bounds[1, 1] - bounds[0, 1] - 4
        vertices[:, 1] += bounds[0, 1] + 2

        # Generate convex hull
        hull = ConvexHull(vertices).vertices
        return vertices[hull]

    @staticmethod
    def split_freespace(freespace):
        # Randomly split a list of N free spaces to N + 1 free spaces
        if len(freespace) == 0:
            return
        split_idx = int(np.random.rand() * (len(freespace) - 1))

        freespace_box = freespace[split_idx] # [[min_x, min_y], [max_x, max_y]]

        # Randomly choose horizontal versus vertical split
        horizontal_prob = np.random.rand(1)
        axis = 0
        if horizontal_prob > 0.5:
            axis = 1
        
        split_coordinate = np.random.rand() * (freespace_box[1, axis] - freespace_box[0, axis]) + freespace_box[0, axis]

        # Make a new box with the coordinates on one-side of the split
        box_1 = freespace_box.copy()
        box_2 = freespace_box.copy()

        # set maximum
        box_1[1, axis] = split_coordinate
        # set minimum
        box_2[0, axis] = split_coordinate

        freespace[split_idx] = box_1
        freespace.append(box_2)


    @staticmethod
    def make_random(bounds, num_vertices, return_num_made=False):
        """Makes a random disjoint set of convex polygons within the bounds
        and with num_vertices vertices in total."""
        # print("Generating Random polygons")
        free_space = [np.array([[bounds[0], bounds[1]], [bounds[2], bounds[3]]])]
        # Randomly split a few times to start 
        for _ in range(int(0.3 * num_vertices)):
            Polygons.split_freespace(free_space)

        polygons = []
        vertices_generated = 0
        while vertices_generated < num_vertices and (num_vertices - vertices_generated)  > 2:
            # Randomly split free_space
            if len(free_space) < 3:
                Polygons.split_freespace(free_space)

            # Choose a random section large enough to reasonably hold a polygon
            found_freespace = False
            while not found_freespace:
                # print(len(free_space))
                if len(free_space) == 0:
                    break
                fill_idx = int(np.random.rand() * (len(free_space) - 1))
                box = free_space[fill_idx]
                free_space.pop(fill_idx)
                if box[1, 0] - box[0, 0] > 10 and box[1, 1] - box[0, 1] > 10:
                    found_freespace = True
            
            # In case all free space is taken up
            if not found_freespace:
                break

            verts_left = num_vertices - vertices_generated
            polygon = Polygons.make_convex(verts_left, box)
            polygons.append(polygon)
            vertices_generated += len(polygon)

        # print("Finished with: {} Polygons".format(len(polygons)))
        if not return_num_made:
            return polygons
        else:
            return polygons, vertices_generated


    def merge_intersecting(self):
        """Merge intersecting polygons into a single polygon."""
        pass

    def random_edge_sampler(self):
        """Returns an iterator that randomly samples edges without replacement."""
        # Make edges
        edges = []
        for polygon in self.polygons:
            for i in range(len(polygon)):
                edges.append(np.array([polygon[i], polygon[(i + 1) % len(polygon)]]))
        
        # Get a random shuffling of edge indices
        indices = [i for i in range(len(edges))]
        random.shuffle(indices)
        for i in indices:
            yield edges[i]
        
    def __getitem__(self, idx):
        return self.polygons[idx]


    def contains_trap(self, trap):
        """Returns whether a polygon surrounds all points."""
        points = trap.raw()
        for poly in self.polygons:
            # TODO First check that the bounding boxes overlap to reduce time complexity

            contained = np.zeros(len(points)).astype(bool)
            for idx in range(len(poly)):
                edge = make_lr(np.array([poly[idx], poly[(idx + 1) % len(poly)]]))
                # Check each point to see if they lie on the edge
                for i, point in enumerate(points):
                    contained[i] = contained[i] or point_on_edge(edge, point)
            # print("[contained] {}".format(contained))

            if contained.all():
                return True

        return False
