
import unittest
from src.point_location import *
from src.structures import *
import numpy as np
from numpy import array


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
        self.assertEqual(len(point_locator.trapezoids.right_adjacent(7)), 1)
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
        bouns = [10, 10, 4029.0, 4029.0] 
        edges = [array([[ 325.71918489, 4017.59875984],
            [ 384.11599509, 3996.69930812]]), array([[340.72813137,  37.78581305],
            [378.96155402, 267.41253854]]), array([[312.4139203 , 937.06293957],
            [808.51331707, 926.81504824]]), array([[397.85351628, 496.50165699],
            [405.17648402, 540.95978716]]), array([[1424.95518442, 1043.53417585],
            [1450.03160567, 1153.11433987]]), array([[  96.55398972, 4000.31744829],
            [ 175.49472021, 4020.93778897]]), array([[2719.44540336,  893.45312542],
            [2720.82772452,  905.91512422]]), array([[2738.17138006,  843.01187128],
            [3921.16940483,  842.88451496]]), array([[ 808.51331707,  926.81504824],
            [1086.86822411,  930.68530377]]), array([[2162.63511247, 1238.36306499],
            [2163.26408985, 1243.53470662]]), array([[ 236.75378145, 1339.83699084],
            [ 689.70479652, 1347.81977364]]), array([[1028.24951139, 2618.53570427],
            [1090.41406178, 2597.72949836]]), array([[3979.08535327,  585.2401302 ],
            [4022.87926456,  691.44712238]]), array([[ 398.36853596, 3967.07004953],
            [ 401.17864299, 3851.54332654]]), array([[4016.92279632,  876.41904746],
            [4017.74220545,  867.53745405]]), array([[ 894.43971093, 1344.08558993],
            [1134.4513517 , 1163.44503421]]), array([[1277.23162103,  965.61901221],
            [1392.25595998,  995.62577825]]), array([[3713.53877195,  877.42354087],
            [3795.93682867,  877.30887325]]), array([[1086.86822411,  930.68530377],
            [1096.69151066,  937.42622481]]), array([[3020.21866296,  882.57962816],
            [3526.81616092,  884.06459242]]), array([[1199.21833987,  988.12542384],
            [1277.23162103,  965.61901221]]), array([[2236.89781566,  853.63285895],
            [2242.02295198,  875.49277454]]), array([[2765.66276543,  889.77227027],
            [2809.90733783,  887.86765421]]), array([[2854.45046882,  822.73217114],
            [3236.10860966,  791.61464258]]), array([[ 175.49472021, 4020.93778897],
            [ 305.86533576, 4022.68619149]]), array([[1190.93363067,  899.64643222],
            [1243.92367144,  920.65985753]]), array([[3543.26012205,  917.79352669],
            [3561.9359357 ,  903.45301567]]), array([[ 306.03438566, 3369.14884887],
            [ 367.22541333, 3410.03943339]]), array([[576.96313586,  98.63750615],
            [583.36571293, 224.27254117]]), array([[2894.02408881, 3945.07266901],
            [3809.35027934, 3945.17054801]]), array([[2735.28199056,  917.50303669],
            [2826.78295209,  921.81136714]]), array([[1528.06592042,  860.00917258],
            [1534.29862813,  795.74660797]]), array([[1515.31119025, 2805.844158  ],
            [2083.58672773, 2740.10412963]]), array([[3236.10860966,  791.61464258],
            [3271.29660582,  606.33724381]]), array([[389.0295805 , 296.89295056],
            [392.15883861,  17.48310277]]), array([[2720.82772452,  905.91512422],
            [2735.28199056,  917.50303669]]), array([[1392.25595998,  995.62577825],
            [1424.95518442, 1043.53417585]]), array([[1491.90139424,  588.73824553],
            [1501.71993117,  606.19253976]]), array([[389.0295805 , 296.89295056],
            [397.85351628, 496.50165699]]), array([[1165.60046689,  751.97006557],
            [1177.44186808,  581.58098385]]), array([[2844.0888358 , 4022.64203988],
            [3901.47680773, 4024.48301447]]), array([[3964.29560768,  819.2957501 ],
            [4006.19279105,  787.5410441 ]]), array([[1493.87408795,  911.80136879],
            [1528.06592042,  860.00917258]]), array([[3733.93489405,  819.20617063],
            [3964.29560768,  819.2957501 ]]), array([[ 689.70479652, 1347.81977364],
            [ 894.43971093, 1344.08558993]]), array([[ 18.59894705, 386.57450741],
            [ 25.11082465, 105.69213865]]), array([[372.55977427, 563.49365315],
            [380.65782209, 555.01405304]]), array([[ 611.45240273, 2773.3302009 ],
            [1028.24951139, 2618.53570427]]), array([[2706.05718848, 3950.41485316],
            [2894.02408881, 3945.07266901]]), array([[  24.11967384, 3872.25035831],
            [  31.1720607 , 3936.133321  ]]), array([[1163.91783867,  853.25790883],
            [1165.60046689,  751.97006557]]), array([[ 373.92888748, 3423.93956127],
            [ 381.58559617, 3439.89639662]]), array([[1482.22913393, 1246.70938145],
            [1484.85522836, 1257.70059021]]), array([[1531.76725463,  690.23565452],
            [1534.29862813,  795.74660797]]), array([[1163.91783867,  853.25790883],
            [1190.93363067,  899.64643222]]), array([[ 152.81523716, 3380.15956171],
            [ 306.03438566, 3369.14884887]]), array([[ 898.93733263,  530.63371266],
            [2647.36809636,  557.57188363]]), array([[3312.01094563,  812.75086141],
            [3488.53279187,  817.59598346]]), array([[ 398.84539414, 3717.87032245],
            [ 401.17864299, 3851.54332654]]), array([[ 18.59894705, 386.57450741],
            [159.77452446, 539.47477773]]), array([[  43.94085934, 1203.63176706],
            [  65.65023279, 1308.47194028]]), array([[240.37824558,  14.54646564],
            [340.72813137,  37.78581305]]), array([[2100.74772808,  943.54772169],
            [2162.63511247, 1238.36306499]]), array([[3983.78898213,  845.2051654 ],
            [4017.74220545,  867.53745405]]), array([[3940.16610147, 4019.0198934 ],
            [3978.49582603, 3989.85378633]]), array([[  13.7208945 , 3695.37541383],
            [  24.11967384, 3872.25035831]])]        