""" Function and helpers to take a polygon and triangulate it """

def triangulate_polygon(self, polygon):
    """
    Args:
        polygon(np.ndarray): (N, 2) array of polygon points.
    returns:
        triangles(np.ndarray): (M, 3, 2) array of M triangles.
    """
    pass

def partition_monotone(self, polygon):
    """
    Args: 
        polygon(np.ndarray): (N, 2) array of polygon points.
    returns:
        monotone(np.ndarray): (M, P, 2) M monotone polygons. A 
                monotone polygon is one such that any intersection of a line and 
                the polygon results in a connected polygon.
    """
    pass

def compute_vertex_labels(self, polygon):
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
    labels = np.zeros(polygon.shape[0])

    # start at the top-most vertex
    start_vertex = np.argmax(polygon[:, 1])
    last_vertex = polygon[start_vertex]
    labels[start_vertex] = 0
    for i in range(len(polygon)):
        idx = idx + start_vertex % len(polygon)


