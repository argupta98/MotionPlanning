""" Function to compute the Configuration Space from obstacle + vehicle polygons. """
from scipy.spatial import ConvexHull
import numpy as np
from sortedcontainers import SortedDict, SortedList
from .structures import Polygons
from .point_location import PointLocator

def compute_cspace(obstacle_polygons, vehicle_polygon):
    """ Computes the configuration space of a set of polygons

    Args:
        obstacle_polygons (list): A list of (T, 2) numpy arrays with the polygon representation of obstacles.
            polygons must be convex.
        vehicle_polygon (np.ndarray): A (N, 2) array of points representing the (convex) shape of the vehicle.
    """

    enlarged_obstacles = []
    for obstacle in obstacle_polygons:
        enlarged_obstacles.append(minkowski_sum(obstacle, vehicle_polygon))
    
    # TODO: merge intersecting polygons into one.

    # TODO: Compute Trapezoid Decomposition
    return enlarged_obstacles

def trapezoid_decomposition_linear(polygons):
    """
    Keep track of which lines to add to GUI, keep track of the point_vertices.
    """
    # Enumerate all the edges and iteratively build up the set of trapezoids
    # Add a vertical line for each point in the polygon
    all_polygons = np.concatenate(polygons, axis=0)
    vertical_lines = SortedDict({x[0]: [x[1], 1000000, 0] for x in all_polygons})

    # Loop over Polygons to determine end-points
    for polygon in polygons:
        start_vertex = polygon[0]
        for vertex in polygon[1:]:
            # find the lines in front of the smaller 
            x_start = start_vertex[0]
            x_curr = vertex[0]
            start_idx = vertical_lines.bisect_right(min(x_start, x_curr))
            end_idx = vertical_lines.bisect_left(max(x_start, x_curr))
            x_vals = vertical_lines.keys()
            for i in range(start_idx, end_idx):
                x = x_vals[i]
                if x < min(x_start, x_curr) or x > max(x_start, x_curr):
                    continue
                y, top, bottom = vertical_lines[x]
                y_val = linear_interpolation(start_vertex, vertex, x)
                if y_val > y and y_val < top:
                    vertical_lines[x][1] = y_val
                elif y_val < y and y_val > bottom:
                    vertical_lines[x][2] = y_val
            start_vertex = vertex
    return vertical_lines


def trapezoid_decomposition_pl(polygons, bounds):
    """ Runs polygon decomposition while maintaining the 
        point location datastructure for O(nlogn) runtime."""
    polygons = Polygons(polygons)
    point_locator = PointLocator(bounds)
    for edge in polygons.random_edge_sampler():
        point_locator.add_line(edge)
    return point_locator


def freespace_graph(trapezoids):
    """
    Computes a Graph of rechable freespace nodes from 
    a set of trapezoids.
    """
    pass

def linear_interpolation(p_1, p_2, x):
    slope = (p_1[1] - p_2[1]) / (p_1[0] - p_2[0])
    x_offset = x - p_2[0]
    return p_2[1] + slope * x_offset
            

def minkowski_sum(obstacle, vehicle):
    """ Computes minkowski sum to inflate the obstacle polygon in O(M + N).

    Args:
        obstacle_polygons (np.ndarray): An (M, 2) numpy array with the polygon representation of obstacles.
        vehicle_polygon (np.ndarray): An (N, 2) array of points representing the (convex) shape of the vehicle.
    """

    vehicle = vehicle.astype(np.float32)
    # Center the vehicle at (0, 0)
    vehicle -= vehicle.mean(axis=0)

    # flip the vehicle
    vehicle = -vehicle

    # Add all points into one large shape
    minkowski_shape = []
    for point in obstacle:
        minkowski_shape.append(point + vehicle)

    minkowski_shape = np.concatenate(minkowski_shape, axis=0)

    # Compute the convex hull
    hull = ConvexHull(minkowski_shape).vertices
    return minkowski_shape[hull]

