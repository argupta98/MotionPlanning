"""Contains the classes for working with the polygons and the trapezoids in a coherent way."""

import numpy as np
import random
from matplotlib.path import Path
from line_utils import *

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
            print("[contained] {}".format(contained))

            if contained.all():
                return True

        return False
