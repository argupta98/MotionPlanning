""" Some common utility functions for lines. """
import numpy as np

def slope(edge):
    """Returns the slope of the edge"""
    return float(edge[0][1] - edge[1][1]) / float(edge[0][0] - edge[1][0])

def linear_interpolation(edge, x):
    """Interpolates the edge to get the y value at the provided x coordinate"""
    assert(edge[0, 0] <= edge[1, 0])
    # Check segment bounds
    if x < edge[0, 0] - 0.000001:
        return -1000000000
    if x > edge[1, 0] + 0.0000001:
        return -1000000000

    m = slope(edge)
    if m != 0:
        b = edge[0][1] - m * edge[0][0]
        return m * x + b
    else:
        assert(edge[0][1] == edge[1][1])
        return edge[0][1]

def make_lr(edge):
    """Makes and edge so that the left point is first."""
    if len(edge) == 1:
        return edge
    left_idx = np.argmin(edge[:, 0])
    return np.array([edge[left_idx], edge[1 - left_idx]])

def normal(edge):
    """Returns the normal of the edge."""
    dy = edge[1, 1] - edge[0, 1]
    dx = edge[1, 0] - edge[0, 0]
    return np.array([-dy, dx])

def point_on_edge(edge, point):
    if edge[0, 0] < edge[1, 0]:
        y_val = linear_interpolation(edge, point[0])
        return np.allclose(y_val, point[1])
    else:
        return point[1] <= np.max(edge[:, 1]) and point[1] >= np.min(edge[:, 1])