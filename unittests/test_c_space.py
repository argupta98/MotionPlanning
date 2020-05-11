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
    
    def test_random(self):
        # check a bunch of random examples
        for _ in range(1000):
            m_p_n = 100
            m = int(np.random.rand() * (m_p_n - 6)) + 3
            n = m_p_n - m
            bounds = [10, 10, 790, 790]
            bounds = np.array([[bounds[0], bounds[1]], [bounds[2], bounds[3]]])
            polygon_vehicle = Polygons.make_convex(m, bounds)
            polygon_obstacle = Polygons.make_convex(n, bounds)

            #  true_complexity = len(polygon_vehicle) + len(polygon_obstacle)
            output = minkowski_sum_fast(polygon_obstacle, polygon_vehicle)
            expected = minkowski_sum(polygon_obstacle, polygon_vehicle)
            """
            print("output: \n{}".format(output))
            print("expected: \n{}".format(expected))
            for x in expected:
                self.assertTrue(x in output, "{} not in output".format(x))
            """
            

    

