"""Contains the classes for working with the polygons and the trapezoids in a coherent way."""

import numpy as np
import random

class Polygons(object):
    """ A class to hold several polygons and implements useful polygon operations."""

    def __init__(self, polygons):
        """
        Args:
            polygons (list): a list of (P,2) np.ndarrays which represent individual polygons.
        """
        self.polygons = polygons
    
    def counter_clock(self):
        """Set the vertices to go in conter-clockwise order."""
        pass

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

    def edges_for_vertex(self, poly_idx, vertex):
        """Returns the neighboring edges of the vertex."""
        pass

    def edges_for_vertex_idx(self, poly_idx, vertex_idx):
        """Returns the neighboring edges of the vertex."""
        pass
