
""" Implements Timing Cases for PointLocation Building and Querying. """

from .timer_base import *
from src.c_space import *
import numpy as np
from src.structures import Polygons

# Decomposition Cases
class MinkowskiCases(Timer):
    # Specific cases  
    CASES = [([3 * i, [10, 10, 790 * i * 10.0, 790 * i * 10.0]]) for i in range(3, 10000, 100)]

    def __init__(self, use_slow=False):
        if use_slow:
            super(MinkowskiCases, self).__init__(minkowski_sum)
            self.fn_name = "Minkowski Sum O(mn)"
        else:
            super(MinkowskiCases, self).__init__(minkowski_sum_fast)
            self.fn_name = "Minkowski Sum"
        self.slow = True
        self.complexity_name = "O(m + n)"
    
    def make_input(self, case):
        # Pick a random partition to split into m, n
        m_p_n = case[0]
        m = int(np.random.rand() * (m_p_n - 6)) + 3
        n = m_p_n - m
        bounds = case[1]
        bounds = np.array([[bounds[0], bounds[1]], [bounds[2], bounds[3]]])
        polygon_vehicle = Polygons.make_convex(m, bounds)
        polygon_obstacle = Polygons.make_convex(n, bounds)

        true_complexity = len(polygon_vehicle) + len(polygon_obstacle)
        return true_complexity, (polygon_obstacle, polygon_vehicle)
    
    def complex_fn(self, values):
        """ O(m + n) """
        return values
    
    def plot_complexity(self, values):
        return values

    def run(self):
        self.run_suite(self.CASES)