import unittest
from src.c_space import *

class TestCSpace(unittest.TestCase):

    def test_minkowski(self):
        # A simple testcase to ensure that the minkowski sum alg is running properly
        triangle = np.array([[200, 100],
                             [300, 100],
                             [250, 0]])

        square = np.array([[400, 50],
                           [800, 50],
                           [800, 200],
                           [400, 200]])
        
        output = minkowski_sum_fast(triangle, square)
