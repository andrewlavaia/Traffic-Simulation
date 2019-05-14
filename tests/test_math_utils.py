import unittest
import math
import math_utils


class TestRotateAroundPoint(unittest.TestCase):
    def test_90_degree_rotation(self):
        point = (1, 0)
        degrees = 90
        expected = (0, 1)
        result = math_utils.rotate_point(point, degrees)
        self.assertAlmostEqual(expected[0], result[0], places=10)
        self.assertAlmostEqual(expected[1], result[1], places=10)

    def test_45_degree_rotation(self):
        point = (1, 0)
        degrees = 45
        expected = (math.sqrt(2)/2, math.sqrt(2)/2)
        result = math_utils.rotate_point(point, degrees)
        self.assertAlmostEqual(expected[0], result[0], places=10)
        self.assertAlmostEqual(expected[1], result[1], places=10)

    def test_0_degree_rotation(self):
        point = (1, 0)
        degrees = 0
        expected = (1, 0)
        result = math_utils.rotate_point(point, degrees)
        self.assertAlmostEqual(expected[0], result[0], places=10)
        self.assertAlmostEqual(expected[1], result[1], places=10)

    def test_360_degree_rotation(self):
        point = (1, 0)
        degrees = 1080
        expected = (1, 0)
        result = math_utils.rotate_point(point, degrees)
        self.assertAlmostEqual(expected[0], result[0], places=10)
        self.assertAlmostEqual(expected[1], result[1], places=10)

    def test_90_degree_rotation_around_point(self):
        point = (5, 3)
        center_point = (3, 3)
        degrees = 90
        expected = (3, 5)
        result = math_utils.rotate_point(point, degrees, center_point)
        self.assertAlmostEqual(expected[0], result[0], places=10)
        self.assertAlmostEqual(expected[1], result[1], places=10)

    def test_45_degree_rotation_around_point(self):
        point = (5, 3)
        center_point = (3, 3)
        degrees = 45
        expected = (3 + math.sqrt(2), 3 + math.sqrt(2))
        result = math_utils.rotate_point(point, degrees, center_point)
        self.assertAlmostEqual(expected[0], result[0], places=10)
        self.assertAlmostEqual(expected[1], result[1], places=10)

    def test_0_degree_rotation_around_point(self):
        point = (5, 3)
        center_point = (3, 3)
        degrees = 0
        expected = (5, 3)
        result = math_utils.rotate_point(point, degrees, center_point)
        self.assertAlmostEqual(expected[0], result[0], places=10)
        self.assertAlmostEqual(expected[1], result[1], places=10)
