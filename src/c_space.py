""" Function to compute the Configuration Space from obstacle + vehicle polygons. """
from scipy.spatial import ConvexHull
import numpy as np
from sortedcontainers import SortedDict, SortedList
from .structures import Polygons, Polygon
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
        enlarged_obstacles.append(minkowski_sum_fast(obstacle, vehicle_polygon))
    
    # TODO: merge intersecting polygons into one.

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
    """ Computes minkowski sum to inflate the obstacle polygon in O(MN).

    Args:
        obstacle_polygons (np.ndarray): An (M, 2) numpy array with the polygon representation of obstacles.
        vehicle_polygon (np.ndarray): An (N, 2) array of points representing the shape of the vehicle.
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


def minkowski_sum_fast(obstacle, vehicle):
    """ Computes minkowski sum to inflate the obstacle polygon in O(M + N).

    Args:
        obstacle_polygons (np.ndarray): An (M, 2) numpy array with the polygon representation of obstacles.
        vehicle_polygon (np.ndarray): An (N, 2) array of points representing the shape of the vehicle.
    """

    vehicle = Polygon(-vehicle.astype(np.float32))
    obstacle = Polygon(obstacle)

    # Convert both shapes to go counter-clockwise
    vehicle.counterclockwise()
    obstacle.counterclockwise()

    # get the proper edge ordering based on the 
    vehicle_edge_angles, v_start = vehicle.edge_angles()
    obstacle_edge_angles, o_start = obstacle.edge_angles()
    print("vehicle edge angles: {}".format(vehicle_edge_angles))
    print("obstacle edge angles: {}".format(obstacle_edge_angles))

    # Start with obstacle points to get the right location
    output_polygon = [obstacle.edges[o_start, 0], obstacle.edges[o_start, 1]]
    start_angle = obstacle_edge_angles[o_start]
    last_angle = obstacle_edge_angles[o_start]
    print("obstacle start: {}".format(start_angle))

    # quick linear scan to find the next larger angle in vehicle
    while vehicle_edge_angles[v_start] < last_angle:
        v_start =  (v_start + 1) % len(vehicle_edge_angles)

    o_idx = 1
    v_idx = 0

    # Add all points into one large shape
    for _ in range(1, len(vehicle_edge_angles) + len(obstacle_edge_angles)):
        # Transform to the correct value
        curr_v_idx = (v_idx + v_start) % len(vehicle_edge_angles)
        curr_o_idx = (o_idx + o_start) % len(obstacle_edge_angles)
        print("curr_v_idx: {}".format(curr_v_idx))
        print("curr_o_idx: {}".format(curr_o_idx))
        # angle_v = 1000
        #angle_o = 1000
        #if v_idx < len(vehicle_edge_angles):
        angle_v = vehicle_edge_angles[curr_v_idx]
        # if o_idx < len(obstacle_edge_angles):
        angle_o = obstacle_edge_angles[curr_o_idx]

        print("angle_v: {}".format(angle_v))
        print("angle_o: {}".format(angle_o))
        # Get angular difference        
        diff_v = angle_v - last_angle
        diff_o = angle_o - last_angle
        if diff_v < 0:
            diff_v = diff_v + 2 * np.pi
        if diff_o < 0:
            diff_o = diff_o + 2 * np.pi

        edge = None 
        if diff_v < diff_o:
            print("chose v!")
            edge = vehicle.edges[curr_v_idx]
            v_idx += 1
            last_angle = angle_v
        else:
            print("chose o!")
            edge = obstacle.edges[curr_o_idx]
            o_idx += 1
            last_angle = angle_o
        
        edge_vector = edge[1] - edge[0]
        output_polygon.append(output_polygon[-1] + edge_vector)

    assert(v_idx == len(vehicle.edges))
    assert(o_idx == len(obstacle.edges))

    return np.array(output_polygon)


