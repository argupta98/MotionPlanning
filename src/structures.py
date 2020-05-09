"""Contains the classes for working with the polygons and the trapezoids in a coherent way."""

import numpy as np
import random
from matplotlib.path import Path

class Polygon(object):
    """ A class with useful polygon functions."""
    def __init__(self, points):
        self.points = points
        self.path_repr = Path(points, closed=True)

    def counter_clock(self):
        """Set the vertices to go in conter-clockwise order."""
        pass

    def edges_for_vertex(self, vertex):
        """Returns the neighboring edges of the vertex."""
        pass

    def edges_for_vertex_idx(self, vertex_idx):
        """Returns the neighboring edges of the vertex."""
        pass

    def points_in(self, vertex_idx):
        """Returns whether or not the vertex points into the polygon."""
        pass

    
    def __len__(self):
        return len(self.points)

    def __getitem__(self, idx):
        return self.points[idx]

class Polygons(object):
    """ A class to hold several polygons and implements useful polygon operations."""

    def __init__(self, polygons):
        """
        Args:
            polygons (list): a list of (P,2) np.ndarrays which represent individual polygons.
        """
        self.polygons = polygons
        self.path_repr_polygons = []
        for poly in polygons:
            self.path_repr_polygons.append(Path(poly, closed=True))
    
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

    def contains(self, points):
        """Returns whether a polygon surrounds all points."""
        for poly in self.path_repr_polygons:
            contains = poly.contains_points(points, radius=-0.01)
            print("contains: {}".format(contains))
            if contains.all():
                return True
        return False
