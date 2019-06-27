import unittest
import collision


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.grid = collision.Grid(32, 32, -1024, 1024, -768, 768)

    def test_find_cell_num_first(self):
        actual = self.grid.getCellNum(-1024, -768)
        expected = 0
        self.assertEqual(actual, expected)

    def test_find_cell_num_last(self):
        actual = self.grid.getCellNum(1023.99, 767.99)
        expected = self.grid.num_rows * self.grid.num_cols - 1
        self.assertEqual(actual, expected)

    def test_find_cell_num_oob(self):
        actual = self.grid.getCellNum(1025, 767)
        expected = -1
        self.assertEqual(actual, expected)

    def test_find_cell_num_mid(self):
        mid_x = self.grid.x_min + (self.grid.x_max - self.grid.x_min)/2
        mid_y = self.grid.y_min + (self.grid.y_max - self.grid.y_min)/2
        actual = self.grid.getCellNum(mid_x, mid_y)
        expected = (self.grid.num_cols * self.grid.num_rows/2) + self.grid.num_cols/2
        self.assertEqual(actual, expected)
