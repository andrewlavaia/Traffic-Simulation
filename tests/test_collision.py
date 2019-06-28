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


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.quad = collision.QuadTree(-1024, 1024, -768, 768)
        self.quad.insertIntoCell(10, 10, "A")
        self.quad.insertIntoCell(15, 10, "B")
        self.quad.insertIntoCell(20, 20, "C")
        self.quad.insertIntoCell(-1, 10, "D")

    def test_find_all_objects_in_same_cell(self):
        actual = self.quad.getCellContents(5, 5)
        expected = {"A", "B"}
        self.assertEqual(actual, expected)

        actual = self.quad.getCellContents(20, 20)
        expected = {"C"}
        self.assertEqual(actual, expected)

        actual = self.quad.getCellContents(-1, 10)
        expected = {"D"}
        self.assertEqual(actual, expected)

    def test_find_no_objects_in_empty_cell(self):
        actual = self.quad.getCellContents(-500, -350)
        expected = None
        self.assertEqual(actual, expected)
