import unittest
from src.c_space import *

class TestCSpace(unittest.TestCase):

    def test_minkowski(self):
        # A simple testcase to ensure that the minkowski sum alg is running properly
        triangle = np.array([[200, 100],
                             [300, 100],
                             [250, 10]])

        square = np.array([[400, 50],
                           [800, 50],
                           [800, 200],
                           [400, 200]])
        
        output = minkowski_sum_fast(square, triangle)
        expected = np.array([[400., 260.],
                            [800., 260.],
                            [850., 170.],
                            [850.,  20.],
                            [450.,  20.],
                            [350.,  20.],
                            [350., 170.]])

        print(output)
        first_idx = output[0]
        offset = 0
        for i, val in expected:
            if np.allclose(first_idx, val):
                offset = i
        expected = np.roll(expected, offset)
        np.testing.assert_equal(output, expected)
    

