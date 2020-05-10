""" Implements Timing Cases for PointLocation Building and Querying. """

from .timer_base import *
from src.c_space import *
import numpy as np
from src.structures import Polygons

# Decomposition Cases
class DecompositionCases(Timer):
    # Specific cases  
    CASES = [[3 * i, [10, 10, 790 * i/10.0, 790 * i / 10.0]] for i in range(1, 500, 10)]

    def __init__(self):
        super(DecompositionCases, self).__init__(trapezoid_decomposition_pl)
        self.complexity_name = "O(nlogn)"
        self.fn_name = "Trapezoid Decomposition"
    
    def make_input(self, case):
        polygons, num_vertices = Polygons.make_random(case[1], case[0], return_num_made=True)
        return num_vertices, (polygons, case[1])
    
    def complex_fn(self, values):
        """ O(NlogN) """
        return values * np.log(values)

    def run(self):
        self.run_suite(self.CASES)
