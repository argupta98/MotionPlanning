""" Implements Timing Cases for PointLocation Building and Querying. """

from .timer_base import *
from src.c_space import *
import numpy as np
from src.structures import Polygons

# Decomposition Cases
class QueryCases(Timer):
    # Specific cases  
    CASES = [[3 * i, [10, 10, 790 * i/10.0, 790 * i / 10.0]] for i in range(1, 500, 25)]

    def __init__(self):
        super(QueryCases, self).__init__(self.query)
        self.complexity_name = "O(logn)"
        self.fn_name = "Point Location Query"
    
    def query(self, pl, point):
        return pl.query(point)

    
    def make_input(self, case):
        vertices, bounds = case
        polygons, num_vertices = Polygons.make_random(bounds, vertices, return_num_made=True)
        # print(bounds)
        pointlocator = trapezoid_decomposition_pl(polygons, bounds)

        random_point = np.random.rand(2) * (case[1][3] - case[1][0] - 20) + case[1][0] + 10
        return num_vertices, (pointlocator, random_point)
    
    def complex_fn(self, values):
        """ O(logN) """
        return np.log(values)

    def plot_complexity(self, values):
        return values

    def run(self):
        self.run_suite(self.CASES)
