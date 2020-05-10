"""Contains the classes for working with the polygons and the trapezoids in a coherent way."""

import numpy as np
import random
from matplotlib.path import Path
from scipy.spatial import ConvexHull
from line_utils import *


class Polygons(object):
    """ A class to hold several polygons and implements useful polygon operations."""

    def __init__(self, polygons):
        """
        Args:
            polygons (list): a list of (P,2) np.ndarrays which represent individual polygons.
        """
        self.polygons = polygons
    
    @staticmethod
    def split_freespace(freespace):
        # Randomly split a list of N free spaces to N + 1 free spaces
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
    def make_random(bounds, num_vertices):
        """Makes a random disjoint set of convex polygons within the bounds
        and with num_vertices vertices in total."""
        print("Generating Random polygons")
        free_space = [np.array([[bounds[0], bounds[1]], [bounds[2], bounds[3]]])]
        # Randomly split a few times to start 
        for _ in range(20):
            Polygons.split_freespace(free_space)

        polygons = []
        vertices_generated = 0
        while vertices_generated < num_vertices and (num_vertices - vertices_generated)  > 2:
            # Randomly split free_space
            if len(free_space) < 3:
                Polygons.split_freespace(free_space)

            # Choose a random section
            found_freespace = False
            while not found_freespace:
                fill_idx = int(np.random.rand() * (len(free_space) - 1))
                box = free_space[fill_idx]
                free_space.pop(fill_idx)
                if box[1, 0] - box[0, 0] > 10 and box[1, 1] - box[0, 1] > 10:
                    found_freespace = True

            # Fill with the remaining vertices
            verts_left = num_vertices - vertices_generated
            vertices = np.random.rand(verts_left, 2)
            vertices[:, 0] *= (box[1, 0] - box[0, 0]) - 4
            vertices[:, 0] += box[0, 0] + 2 
            vertices[:, 1] *= box[1, 1] - box[0, 1] - 4
            vertices[:, 1] += box[0, 1] + 2

            # Generate convex hull
            hull = ConvexHull(vertices).vertices
            polygons.append(vertices[hull])
            vertices_generated += len(hull)
        print("Finished with: {} Polygons".format(len(polygons)))
        return polygons


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
