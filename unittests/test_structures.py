from src.structures import *
import unittest
import numpy as np

class TestPolygonCounter(unittest.TestCase):
    def test_specific_1(self):
        vehicle= np.array([[-183.49516, -220.11375],
                           [-225.02881, -184.53629 ],
                           [-53.735645, -109.01296 ],
                           [-45.640778, -155.59946 ]])
        vehicle = Polygon(vehicle)
        np.testing.assert_equal(vehicle.edges[0], np.array([[-183.49516, -220.11375],
                                                    [-225.02881, -184.53629 ]]))
        np.testing.assert_equal(vehicle.edges[1], np.array(
                                            [[-225.02881, -184.53629 ],
                                            [-53.735645, -109.01296 ]]))

        np.testing.assert_equal(vehicle.edges[2], np.array(
                                            [[-53.735645, -109.01296 ],
                                            [-45.640778, -155.59946 ]]))

        
        self.assertTrue(vehicle.is_counterclockwise())

        vehicle.counterclockwise()
        self.assertTrue(vehicle.is_counterclockwise())
        angles, _ = vehicle.edge_angles()
        

    def test_specific_2(self):
        square = np.array([[400, 50],
                           [800, 50],
                           [800, 200],
                           [400, 200]])
        vehicle = Polygon(square)
        self.assertFalse(vehicle.is_counterclockwise())
        vehicle.counterclockwise()
        self.assertTrue(vehicle.is_counterclockwise())
        angles, _ = vehicle.edge_angles()
        self.assertEqual(angles[0], 0)
        self.assertEqual(angles[1], np.pi /2)
        self.assertEqual(angles[2], np.pi)
        self.assertEqual(angles[3], 3 * np.pi / 2)

    # def test_edges(self):
    #    square = np.array([[400, 50],
    #                       [800, 50],
    #                       [800, 200],
    #                       [400, 200]])
    #    vehicle = Polygon(square)
    #    np.assertEqual(edges[0], np.array([edges]))
