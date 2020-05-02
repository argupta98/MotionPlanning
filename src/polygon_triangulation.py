""" Function and helpers to take a polygon and triangulate it """
from scipy.spatial import ConvexHull
import numpy as np
from numpy.linalg import norm
from sortedcontainers import SortedDict

def triangulate_polygon(polygon):
    """
    Args:
        polygon(np.ndarray): (N, 2) array of polygon points.
    returns:
        triangles(np.ndarray): (M, 3, 2) array of M triangles.
    """
    pass

def partition_monotone(polygon, labels):
    """
    Args: 
        polygon(np.ndarray): (N, 2) array of polygon points.
    returns:
        monotone(np.ndarray): (M, P, 2) M monotone polygons. A 
                monotone polygon is one such that any intersection of a line and 
                the polygon results in a connected polygon.
    """
    # Sweep Line algorithm

    # Sort polygon by y coordinates
    sorted_indices = np.argsort(polygon[:, 1])

    # Holds the current edges based on their endpoint locations and points to the helper vertex
    current_edges = SortedDict()
    for i in sorted_indices:
        vertex = polygon[i]
        label = labels[i]

        # This is an edge endpoint
        if vertex in current_edges:
            # remove entry from current edges
            pass
        
        # Find the next vertex to add appropriate edges to the queue
        neighbor_indices = np.array([(i-1) % len(polygon), (i+1) % len(polygon)])
        for neighbor in neighbor_indices:
            # Add it to the queue of edges if it has lower y
            if polygon[neighbor, 1] < vertex[1]:
                if neighbor < 0:
                    neighbor += len(polygon)
                # Add to current edges with the current vertex as helper
                current_edges[neighbor] = i
                
        
        # Check for helper change

        # Check for split vertex case
        if label == "split":
            # Add a diagonal to the edge helper
            pass
        



def compute_vertex_labels(polygon):
    """
    Args:
        polygon(np.ndarray): (N, 2) array of polygon points.
    returns:
        labels (list): (N, ) array of vertex labels as 
    """
    labels = ["regular" for _ in range(len(polygon))]

    # start at the top-most vertex
    start_vertex = np.argmax(polygon[:, 1])
    last_vertex = polygon[start_vertex]
    labels[start_vertex] = "start"

    clockwise = False
    if polygon[-1, 0] > polygon[0, 0]:
        clockwise = True

    for i in range(len(polygon)):
        # Check for merge / split
        current_y = polygon[i, 1]
        neighbor_indices = np.array([(i-1) % len(polygon), (i+1) % len(polygon)])
        neighbors_y = polygon[neighbor_indices, 1]
        # Check that The corner points into the polygon
        neighbor_vectors = polygon[neighbor_indices] - polygon[i]
        normal = np.cross(neighbor_vectors[0], neighbor_vectors[1])
        if clockwise:
            normal *= -1
        points_in = normal > 0
        if points_in:
            # If both neighbors are above, then merge vertex
            if current_y < neighbors_y[0] and current_y < neighbors_y[1]:
                labels[i] = "merge"

            # If both neighbors are below, then split vertex
            if current_y > neighbors_y[0] and current_y > neighbors_y[1]:
                labels[i] = "split" 

    return labels


