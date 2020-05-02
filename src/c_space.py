""" Function to compute the Configuration Space from obstacle + vehicle polygons. """
from scipy.spatial import ConvexHull
import numpy as np

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
    return enlarged_obstacles

def minkowski_sum(obstacle, vehicle):
    """ Computes minkowski sum to inflate the obstacle polygon in O(M + N).

    Args:
        obstacle_polygons (np.ndarray): A (M, 2) numpy array with the polygon representation of obstacles.
        vehicle_polygon (np.ndarray): A (N, 2) array of points representing the (convex) shape of the vehicle.
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

