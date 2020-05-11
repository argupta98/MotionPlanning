
import unittest
from src.point_location import *
from src.structures import *
from src.graph import *
import numpy as np
from numpy import array
from tqdm import tqdm


class TestTrapezoidRep(unittest.TestCase):
    def test_three_init(self):
        vertices = np.array([[10, 150], [200, 20], [200, 100]])
        trap = Trapezoid(vertices, originator_vertices=[])
        np.testing.assert_equal(trap.top_line, np.array([[10, 150], [200, 100]]))
        np.testing.assert_equal(trap.bottom_line, np.array([[10, 150], [200, 20]]))
        self.assertEqual(trap.left_p[0], 10)
        self.assertEqual(trap.right_p[0], 200)

    def test_four_init(self):
        vertices = np.array([[10, 10], [200, 20], [200, 100], [10, 300]])
        trap = Trapezoid(vertices, originator_vertices=[])
        np.testing.assert_equal(trap.top_line, np.array([[10, 300], [200, 100]]))
        np.testing.assert_equal(trap.bottom_line, np.array([[10, 10], [200, 20]]))
        self.assertEqual(trap.left_p[0], 10)
        self.assertEqual(trap.right_p[0], 200)
    
    def test_specific_1(self):
        vertices = np.array([[240., 300.],
                             [240., 253.33333333],
                             [100., 300.]])
        trap = Trapezoid(vertices, originator_vertices=[])

        self.assertTrue(np.allclose(trap.bottom_line, np.array([[100, 300], [240, 253.33333333333]])))
        np.testing.assert_equal(trap.top_line, np.array([[100, 300], [240, 300]]))
        self.assertEqual(trap.left_p[0], 100)
        self.assertEqual(trap.right_p[0], 240)
    
    def test_specific_2(self):
        vertices = np.array([[353., 123.98305085],
                             [275., 122.],
                             [275., 790.],
                             [353., 790.]])
        trap = Trapezoid(vertices, originator_vertices=[])
        np.testing.assert_equal(trap.top_line, np.array([[275., 790.], [353., 790.]]))
        self.assertTrue(np.allclose(trap.bottom_line, np.array([[275., 122.], [353., 123.98305085]])))
        self.assertEqual(trap.left_p[0], 275)
        self.assertEqual(trap.right_p[0], 353)
    
    def test_is_left_pointed(self):
        vertices = np.array([[309., 169.],
                            [471., 170.71247357],
                            [471.,  69.]])
        trap = Trapezoid(vertices, originator_vertices=[])
        self.assertTrue(trap.is_left_pointed())


class TestTrapezoidIntersection(unittest.TestCase):
    def test_left_corner(self):
        vertices = np.array([[10, 150], [200, 60], [200, 10]])
        trap = Trapezoid(vertices, originator_vertices=[])
        edge = np.array([[10, 150], [205, 50]])
        self.assertTrue(trap.is_intersected(edge))

    def test_right_corner(self):
        vertices = np.array([[10, 10], [10, 300], [400, 150]])
        trap = Trapezoid(vertices, originator_vertices=[])
        edge = np.array([[0, 100], [400, 150]])
        self.assertTrue(trap.is_intersected(edge))

    def test_left_of_trapezoid(self):
        vertices = np.array([[10, 10], [200, 20], [200, 100], [10, 300]])
        trap = Trapezoid(vertices, originator_vertices=[])
        edge = np.array([[0, 100], [100, 25]])
        self.assertTrue(trap.is_intersected(edge))

    def test_right_of_trapezoid(self):
        pass

    def test_no_intersect(self):
        vertices = np.array([[10, 10], [200, 20], [200, 100], [10, 300]])
        trap = Trapezoid(vertices, originator_vertices=[])
        edge = np.array([[0, 20], [10, 40]])
        self.assertFalse(trap.is_intersected(edge))
    
    def test_top_tangent(self):
        vertices = np.array([[491., 186.],
                            [237., 179.],
                            [237., 790.],
                            [491., 790.]])
        trap = Trapezoid(vertices, originator_vertices=[])
        edge = np.array([[237, 179],
                         [353, 114]])
        self.assertFalse(trap.is_intersected(edge))

    def test_same_upper_right(self):
        vertices = np.array([[295., 138.51724138], 
                            [252., 147.4137931 ],
                            [252., 50.],
                            [295. , 60.]])
        trap = Trapezoid(vertices, originator_vertices=[])
        edge = np.array([[242,  60],
                        [295,  60]])
        self.assertTrue(trap.is_intersected(edge))

class TestTrapezoidsRightAdjacent(unittest.TestCase):
    def test_trapezoids_above(self):
        pass

    def test_trapezoids_below(self):
        pass

    def test_trapezoids_next_to(self):
        pass

    def test_failure_case(self):
        triangles = [np.array([[249, 111],
                    [184, 172],
                    [311, 170]]), np.array([[261, 213],
                    [386, 198],
                    [283, 268]])]
        top_triangle_edges = np.array([[[184, 172], [371, 170]],
                                       [[184, 172], [249, 111]],
                                       [[249, 111], [371, 170]]])
        bottom_triangle_edges = np.array([[[386, 198], [283, 268]], 
                                          [[261, 213], [283, 268]],
                                          [[261, 213], [386, 198]]])
        polygons = Polygons(triangles)

        bounds = [10, 10, 790, 790]
        point_locator = PointLocator(bounds)
        """
        for edge in np.concatenate([top_triangle_edges, bottom_triangle_edges]):
            point_locator.add_line(edge)
        """
        point_locator.add_line(top_triangle_edges[0])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(184)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(371)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 4)

        point_locator.add_line(top_triangle_edges[1])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)),  1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(184)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(249)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(371)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 6)

        point_locator.add_line(top_triangle_edges[2])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)),  1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(184)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(249)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(371)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 7)

        point_locator.add_line(bottom_triangle_edges[0])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)),  1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(184)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(249)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(283)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(371)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(386)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 10)

        point_locator.add_line(bottom_triangle_edges[1])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(184)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(249)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(261)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(283)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(371)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(386)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 12)

        point_locator.add_line(bottom_triangle_edges[2])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(184)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(249)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(261)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(283)), 2)
        print(point_locator.trapezoids.right_adjacent_to(371))
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(371)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(386)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 13)

        point_locator.remove_traps_within_polygons(polygons)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(184)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(249)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(261)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(371)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(283)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(386)), 1)
        
class TestGraphBuilding(unittest.TestCase):
    def test_random(self):
        bounds = [10, 10, 790, 790]
        for _ in tqdm(range(100)):
            random_polygons = Polygons(Polygons.make_random(bounds, 50))
            point_locator = PointLocator(bounds)
            for edge in random_polygons.random_edge_sampler():
                point_locator.add_line(edge)
            graph = Graph(point_locator, 10)
        

class TestIntegration(unittest.TestCase):

    def test_twotriangles(self):
        bounds = [10, 10, 790, 790]
        point_locator = PointLocator(bounds)
        # self.assertEqual(len(point_locator.trapezoids.trapezoids), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        top_triangle_edges = [np.array([[200, 100], [240, 30]]),
                              np.array([[200, 100], [280, 100]]),
                              np.array([[280, 100], [240, 30]])]

        bottom_triangle_edges = [np.array([[100, 300], [400, 300]]),
                                np.array([[100, 300], [400, 200]]),
                                np.array([[400, 300], [400, 200]])]

        point_locator.add_line(top_triangle_edges[0])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        sorted_traps = point_locator.trapezoids.right_adjacent_to(10)
        trap_idx = sorted_traps[sorted_traps.keys()[0]].index
        self.assertEqual(len(point_locator.trapezoids.right_adjacent(trap_idx)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(200)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(240)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 4)

        point_locator.add_line(bottom_triangle_edges[0])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(200)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(100)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(240)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(400)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 7)

        point_locator.add_line(bottom_triangle_edges[1])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(200)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(100)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(240)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(400)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 8)

        point_locator.add_line(top_triangle_edges[1])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(200)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(100)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(240)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(280)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(400)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 10)

        point_locator.add_line(top_triangle_edges[2])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        sorted_traps = point_locator.trapezoids.right_adjacent_to(10)
        trap_idx = sorted_traps[sorted_traps.keys()[0]].index
        self.assertEqual(len(point_locator.trapezoids.right_adjacent(trap_idx)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(200)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(100)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(240)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(280)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(400)), 1)
    
    def test_specific_3(self):
        bounds = [10, 10, 790, 790]
        point_locator = PointLocator(bounds)
        edges = [np.array([[100.41771139, 497.65833091],
                           [193.75398968, 339.39024785]]),
                 np.array([[100.41771139, 497.65833091],
                           [168.82113323, 479.70436783]]),
                 np.array([[168.82113323, 479.70436783],
                          [193.75398968, 339.39024785]])]

        point_locator.add_line(edges[0])
        point_locator.add_line(edges[1])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(168.82113323)), 1)
        point_locator.trapezoids.trap_count()
        # self.assertEqual(len(point_locator.trapezoids.right_adjacent(7)), 1)
        point_locator.add_line(edges[2])
        

    def test_specific_4(self):
        bounds = [10, 10, 79.0, 79.0]
        point_locator = PointLocator(bounds)
        edges = [np.array([[27.54014023, 50.39508477],
       [33.87852725, 21.53020476]]), np.array([[16.20062533, 38.51858695],
       [27.54014023, 50.39508477]]), np.array([[16.20062533, 38.51858695],
       [33.87852725, 21.53020476]])]      
        point_locator.add_line(edges[0])
        point_locator.add_line(edges[1])
        point_locator.trapezoids.trap_count()
        point_locator.add_line(edges[2])
    
    def test_specific_5(self):
        bounds = [10, 10, 790, 790]
        edges = [array([[443, 737],
                    [550, 780]]), array([[309, 169],
                    [471,  69]]), array([[309, 169],
                    [782, 174]]), array([[156, 719],
                    [550, 780]])]
        
        point_locator = PointLocator(bounds)

        point_locator.add_line(edges[0])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(443)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(550)), 1)

        point_locator.add_line(edges[1])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(309)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(443)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(471)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(550)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 7)

        point_locator.add_line(edges[2])
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(10)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(309)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(443)), 2)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(471)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(550)), 1)
        self.assertEqual(len(point_locator.trapezoids.right_adjacent_to(782)), 1)
        self.assertEqual(point_locator.trapezoids.trap_count(), 9)

        point_locator.add_line(edges[3])
                
    def test_random(self):
        bounds = [10, 10, 790, 790]
        for _ in tqdm(range(100)):
            random_polygons = Polygons(Polygons.make_random(bounds, 40))
            point_locator = PointLocator(bounds)
            for edge in random_polygons.random_edge_sampler():
                point_locator.add_line(edge)
