""" Function and helpers to take a polygon and triangulate it """
from scipy.spatial import ConvexHull
import numpy as np
from numpy.linalg import norm

def triangulate_polygon(polygon):
    """
    Args:
        polygon(np.ndarray): (N, 2) array of polygon points.
    returns:
        triangles(np.ndarray): (M, 3, 2) array of M triangles.
    """
    pass

def partition_monotone(polygon):
    """
    Args: 
        polygon(np.ndarray): (N, 2) array of polygon points.
    returns:
        monotone(np.ndarray): (M, P, 2) M monotone polygons. A 
                monotone polygon is one such that any intersection of a line and 
                the polygon results in a connected polygon.
    """
    pass

def compute_vertex_labels(polygon):
    """
    Args:
        polygon(np.ndarray): (N, 2) array of polygon points.
    returns:
        labels (np.ndarray): (N, ) array of vertex labels as 
                0: start
                1: end
                2: regular
                3: split
                4: merge
    """
    labels = ["regular" for _ in range(len(polygon))]

    # start at the top-most vertex
    start_vertex = np.argmax(polygon[:, 1])
    last_vertex = polygon[start_vertex]
    labels[start_vertex] = "start"

    clockwise = False
    if polygon[-1, 0] > polygon[0, 0]:
        clockwise = True

    # Compute Convex hull
    hull = ConvexHull(polygon).vertices
    hull_points = polygon[hull]
    hull_size = len(hull)

    for i in range(len(polygon)):
        # Check for merge / split
        if i not in hull:
            current_y = polygon[i, 1]
            neighbor_indices = np.array([(i-1) % len(polygon), (i+1) % len(polygon)])
            neighbors_y = polygon[neighbor_indices, 1]
            neighbor_vectors = polygon[neighbor_indices] - polygon[i]
            normal = np.cross(neighbor_vectors[0], neighbor_vectors[1])

            if clockwise:
                normal *= -1

            points_in = normal > 0

            if points_in:
                # If both neighbors are above, then merge vertex
                if current_y < neighbors_y[0] and current_y < neighbors_y[1]:
                    # check if the nearest two convex hull points are both above as well
                    labels[i] = "merge"

                # If both neighbors are below, then split vertex
                if current_y > neighbors_y[0] and current_y > neighbors_y[1]:
                    # check if the nearest two convext hull points are both above as well
                    labels[i] = "split" 

    return labels


