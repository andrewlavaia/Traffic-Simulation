import unittest
import graphics


class TestConvertPointToViewFraction(unittest.TestCase):
    def setUp(self):
        self.window = graphics.GraphWin('Test', 1000, 1000)

    def test_x0_y0(self):
        x = 0
        y = 0
        actual = tuple(self.window.convertPointToViewFraction(x, y))
        expected = (0.5, 0.5)
        self.assertEqual(actual, expected)

    def test_min_scrollregion(self):
        x = -self.window.scrollregion_x/2
        y = -self.window.scrollregion_y/2
        actual = tuple(self.window.convertPointToViewFraction(x, y))
        expected = (0, 0)
        self.assertEqual(actual, expected)

    def test_max_scrollregion(self):
        x = self.window.scrollregion_x/2
        y = self.window.scrollregion_y/2
        actual = tuple(self.window.convertPointToViewFraction(x, y))
        expected = (1.0, 1.0)
        self.assertEqual(actual, expected)


class TestGetCoords(unittest.TestCase):
    def setUp(self):
        self.window = graphics.GraphWin('Test', 1024, 768)
        self.window.xview_moveto(0.5)
        self.window.yview_moveto(0.5)
        self.window.zoom_factor = 1.0

    def test_coords_with_default_view(self):
        actual = tuple(self.window.getCoords())
        expected = (0, 768, 1024, 0)
        self.assertEqual(actual, expected)

    def test_coords_with_default_view_after_2x_zoom(self):
        self.window.zoom_factor = 2.0
        actual = tuple(self.window.getCoords())
        x_adj = (self.window.width/2)/self.window.zoom_factor
        y_adj = (self.window.height/2)/self.window.zoom_factor
        expected = (x_adj, 768 - y_adj, 1024 - x_adj, y_adj)
        self.assertEqual(actual, expected)

    def test_coords_with_max_view(self):
        self.window.xview_moveto(1.0)
        self.window.yview_moveto(1.0)
        actual = tuple(self.window.getCoords())
        x_adj = (self.window.width/2)/self.window.zoom_factor
        y_adj = (self.window.height/2)/self.window.zoom_factor
        expected = (0, 768, 1024, 0)
        self.assertEqual(actual, expected)

    def test_coords_with_max_view_after_2x_zoom(self):
        self.window.xview_moveto(0.0)
        self.window.yview_moveto(0.0)
        self.window.zoom_factor = 2.0
        actual = tuple(self.window.getCoords())
        x_adj = (self.window.width/2)/self.window.zoom_factor
        y_adj = (self.window.height/2)/self.window.zoom_factor
        expected = (x_adj, 768 - y_adj, 1024 - x_adj, y_adj)
        self.assertEqual(actual, expected)

    def test_coords_with_min_view(self):
        self.window.xview_moveto(0.0)
        self.window.yview_moveto(0.0)
        actual = tuple(self.window.getCoords())
        x_adj = (self.window.width/2)/self.window.zoom_factor
        y_adj = (self.window.height/2)/self.window.zoom_factor
        expected = (0, 768, 1024, 0)
        self.assertEqual(actual, expected)

    def test_coords_with_min_view_after_2x_zoom(self):
        self.window.xview_moveto(1.0)
        self.window.yview_moveto(1.0)
        self.window.zoom_factor = 2.0
        actual = tuple(self.window.getCoords())
        x_adj = (self.window.width/2)/self.window.zoom_factor
        y_adj = (self.window.height/2)/self.window.zoom_factor
        expected = (x_adj, 768 - y_adj, 1024 - x_adj, y_adj)
        self.assertEqual(actual, expected)


class TestSetCoords(unittest.TestCase):
    def setUp(self):
        self.window = graphics.GraphWin('Test', 1024, 768)
        self.window.xview_moveto(0.5)
        self.window.yview_moveto(0.5)
        self.window.zoom_factor = 1.0

    def test_no_change_to_view_fraction_after_zoom(self):
        self.window.zoom_factor = 2.0
        self.window.setCoords(*self.window.getCoords())
        actual = tuple(self.window.getViewPoint())
        expected = (0, 0)
        self.assertEqual(actual, expected)


class TestToScreen(unittest.TestCase):
    def setUp(self):
        self.window = graphics.GraphWin('Test', 1024, 768)
        self.window.xview_moveto(0.5)
        self.window.yview_moveto(0.5)
        self.window.zoom_factor = 1.0

    def test_00_toscreen_with_default_view_and_default_zoom(self):
        actual = self.window.toScreen(0, 0)
        expected = (0, 0)
        self.assertEqual(actual, expected)

    def test_00_to_screen_with_default_view_and_2x_zoom(self):
        self.window.zoom_factor = 2.0
        self.window.setCoords(*self.window.getCoords())
        print(self.window.getCoords())
        actual = self.window.toScreen(0, 0)
        expected = (-255, -190)  # almost equal -256, -192
        # self.assertEqual(actual, expected)

        actual = self.window.toScreen(512, 384)
        expected = (0, 0)
        # self.assertEqual(actual, expected)

        print(self.window.xview())
        print(self.window.yview())
        print(self.window.getCoords())
        print(self.window.toScreen(0, 0))
        print(self.window.toScreen(256, 192))
        self.window.centerScreenOnPoint(graphics.Point(1024, 768))
        print(self.window.toScreen(256, 192))
        print(self.window.toScreen(1024, 768))


class TestToWorld(unittest.TestCase):
    def setUp(self):
        self.window = graphics.GraphWin('Test', 1024, 768)
        self.window.xview_moveto(0.5)
        self.window.yview_moveto(0.5)
        self.window.zoom_factor = 1.0

    def test_00_toworld_with_default_view_and_default_zoom(self):
        actual = self.window.toWorld(0, 0)
        expected = (0, 0)
        self.assertEqual(actual, expected)

    def test_no_change_from_screen_to_world_and_back(self):
        wx, wy = self.window.toWorld(400, 400)
        sx, sy = self.window.toScreen(wx, wy)
        new_wx, new_wy = self.window.toWorld(sx, sy)
        actual = (int(new_wx), int(new_wy))
        expected = (400, 400)
        self.assertEqual(actual, expected)


class TestZoomAdj(unittest.TestCase):
    def setUp(self):
        self.window = graphics.GraphWin('Test', 1024, 768)
        self.window.xview_moveto(0.5)
        self.window.yview_moveto(0.5)
        self.window.zoom_factor = 1.0

    def test_zoom_adj_no_zoom(self):
        actual = tuple(self.window.getZoomAdj())
        expected = (0, 0)
        self.assertEqual(actual, expected)

    def test_zoom_adj_2x_zoom(self):
        self.window.zoom_factor = 2.0
        actual = tuple(self.window.getZoomAdj())
        expected = (256, 192)
        self.assertEqual(actual, expected)

    def test_zoom_adj_half_zoom(self):
        self.window.zoom_factor = 0.5
        actual = tuple(self.window.getZoomAdj())
        expected = (-512, -384)
        self.assertEqual(actual, expected)

    def test_zoom_adj_same_before_and_after_zoom(self):
        self.window.zoom_factor += 0.1
        actual = tuple(self.window.getZoomAdj())
        expected = (46.54545, 34.90909)
        self.assertAlmostEqual(expected[0], actual[0], places=5)
        self.assertAlmostEqual(expected[1], actual[1], places=5)
        self.window.zoom_factor -= 0.1
        actual = tuple(self.window.getZoomAdj())
        expected = (0, 0)
        self.assertAlmostEqual(expected[0], actual[0], places=5)
        self.assertAlmostEqual(expected[1], actual[1], places=5)


class TestcenterScreenOnPoint(unittest.TestCase):
    def setUp(self):
        self.window = graphics.GraphWin('Test', 1024, 768)
        self.window.xview_moveto(0.5)
        self.window.yview_moveto(0.5)
        self.window.zoom_factor = 1.0

    def test_center_view_on_center_point(self):
        self.window.centerScreenOnPoint(graphics.Point(512, 384))
        actual = tuple(self.window.getViewPoint())
        expected = (0, 0)
        self.assertEqual(actual, expected)

        # confirm view fraction hasn't changed
        xview = self.window.xview()
        yview = self.window.yview()
        actual = (xview[0], yview[0])
        expected = (0.5, 0.5)
        self.assertEqual(actual, expected)

    def test_center_view_on_00(self):
        self.window.centerScreenOnPoint(graphics.Point(0, 0))
        actual = tuple(self.window.getViewPoint())
        expected = (-512, -384)
        self.assertEqual(actual, expected)

    def test_center_view_on_00_after_2x_zoom(self):
        self.window.zoom_factor = 2.0
        self.window.centerScreenOnPoint(graphics.Point(0, 0))
        actual = tuple(self.window.getCenterViewPoint())
        expected = (0, 0)
        self.assertEqual(actual, expected)

    def test_center_view_on_00_before_2x_zoom(self):
        self.window.centerScreenOnPoint(graphics.Point(0, 0))
        self.window.zoom_factor = 2.0
        actual = tuple(self.window.getCenterViewPoint())
        expected = (0, 0)
        self.assertEqual(actual, expected)

    def test_center_view_on_offset_before_2x_zoom(self):
        self.window.centerScreenOnPoint(graphics.Point(1024, 768))
        actual = tuple(self.window.getCenterViewPoint())
        expected = (1024, 768)
        self.assertEqual(actual, expected)

        self.window.zoom_factor = 2.0
        actual = tuple(self.window.getViewPoint())
        expected = (512, 384)
        self.assertEqual(actual, expected)

    def test_center_view_on_offset_after_2x_zoom(self):
        self.window.zoom_factor = 2.0
        self.window.centerScreenOnPoint(graphics.Point(1024, 768))
        actual = tuple(self.window.getCenterViewPoint())
        expected = (1024, 768)
        self.assertEqual(actual, expected)

        actual = tuple(self.window.getViewPoint())
        expected = (512, 384)
        self.assertEqual(actual, expected)
