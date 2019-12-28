from collision import Grid
import graphs
from graphics import Circle, Line, Point, color_rgb, Text
import math_utils


class RoadMap:
    """graphical representation of a graph"""
    def __init__(self, graph, canvas):
        self.canvas = canvas
        self.intersections = {}  # vertex_id: Intersection
        self.roads = {}  # edge_id: Road
        self.route = {}  # vertex_id: Line (used for drawing route)

        # store map objects in a container for quick lookups by location
        num_rows = 128
        num_cols = 128
        x_min = -canvas.scrollregion_x / 2.0
        x_max = canvas.scrollregion_x / 2.0
        y_min = -canvas.scrollregion_y / 2.0
        y_max = canvas.scrollregion_y / 2.0
        self.container = Grid(num_rows, num_cols, x_min, x_max, y_min, y_max)

        for vertex in graph.vertices.values():
            self.intersections[vertex.id] = Intersection(vertex)
            cell = self.container.get_cell_num(vertex.x, vertex.y)
            self.container.insert_into_cell(cell, vertex.id)
            for edge in vertex.get_edges():
                p0 = Point(graph.vertices[edge.source].x, graph.vertices[edge.source].y)
                p1 = Point(graph.vertices[edge.dest].x, graph.vertices[edge.dest].y)

                if edge.is_one_way:
                    self.roads[edge.id] = Road(edge.id, p0, p1, edge.name, edge.lanes)
                else:
                    self.roads[edge.id] = Road2W(edge.id, p0, p1, edge.name, edge.lanes)
                cells = self.container.get_cells_between_two_points(p0, p1)
                for cell in cells:
                    self.container.insert_into_cell(cell, edge.id)

    def get_nearby_object_ids(self, x, y):
        # TODO give precedence to intersections (sort or draw on top or check clicks)
        return self.container.get_cell_contents(x, y)

    def get_obj_by_id(self, obj_id):
        # TODO handle collisions if id in both dicts
        if obj_id in self.intersections:
            return self.intersections[obj_id]
        else:
            return self.roads[obj_id]

    def get_roads_within_view(self):
        x0, y0, x1, y1 = self.canvas.getScreenPoints()
        roads_within_view = set()
        for road in self.roads.values():
            if ((x0 < road.p0.x < x1 and y0 < road.p0.y < y1) or
                    (x0 < road.p1.x < x1 and y0 < road.p1.y < y1)):
                roads_within_view.add(road)
        return roads_within_view

    def draw(self):
        for intersection in self.intersections.values():
            intersection.draw(self.canvas)

        for road in self.roads.values():
            road.draw(self.canvas)

        self.draw_road_names()  # drawn last so road names are on top

    def render_road_names(self):
        # don't redraw new road names every frame, just move the existing ones
        # until road is no longer in view?
        pass

    def draw_road_names(self):
        road_names = {}
        roads_within_view = self.get_roads_within_view()

        for road in roads_within_view:
            road_names[road.name] = road
            road.undraw_text()
            road.draw_text(self.canvas)

    def draw_route(self, car, show_route):
        # TODO optimize to not have to redraw entire route each time
        self.clear_route(self.route)
        self.route = {}

        if not show_route:
            return

        line_width = 3
        line_color = color_rgb(20, 200, 20)
        p0 = Point(car.x, car.y)
        route = car.route[:]
        route.append(car.next_dest_id)
        for vertex_id in route[::-1]:
            intersection = self.intersections[vertex_id]
            p1 = Point(intersection.x, intersection.y)
            line = Line(p0, p1)
            line.setWidth(line_width)
            line.setOutline(line_color)
            self.route[vertex_id] = line
            p0 = p1

        old_route = {key: val for key, val in self.route.items() if key not in route}
        self.route = {key: val for key, val in self.route.items() if key in route}
        self.clear_route(old_route)

        for line in self.route.values():
            line.draw(self.canvas)

    def clear_route(self, route):
        for line in route.values():
            line.undraw()


class Road:
    """graphical representation of a single edge - one way road"""
    def __init__(self, edge_id, p0, p1, name, lanes):
        self.id = edge_id
        self.p0 = p0
        self.p1 = p1
        self.name = name
        self.lanes = lanes
        self.distance = math_utils.distance(p0, p1)

        self.dx = self.p1.x - self.p0.x
        self.dy = self.p1.y - self.p0.y
        self.length = math_utils.pythag(self.dx, self.dy)
        self.unit_x = self.dx / self.length
        self.unit_y = self.dy / self.length

        self.lines = []
        self.width = 2
        self.way_gap = 0  # size of gap between each road direction
        self.lane_gap = 4  # size of gap between lines
        self.click_threshold = self.width * self.lanes

        for i in range(lanes):
            u0 = self.get_lane_adjusted_point(self.p0.x, self.p0.y, i)
            u1 = self.get_lane_adjusted_point(self.p1.x, self.p1.y, i)
            self.lines.append(self.create_line(u0, u1, self.width))
        self.text = self.create_text()

    def __eq__(self, other):
        # This is only used for quickly creating a set of roads by name
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "Road {0}: {1} ({2}, {3}) - ({4}, {5})".format(
            self.id, self.name, self.p0.x, self.p0.y, self.p1.x, self.p1.y
        )

    @staticmethod
    def create_line(p0, p1, width):
        line = Line(p0, p1)
        line.setWidth(width)
        color = color_rgb(200, 200, 200)
        line.setOutline(color)
        line.setArrow("last")
        return line

    def create_text(self):
        midpoint = Point((self.p0.x + self.p1.x)/2.0, (self.p0.y + self.p1.y)/2.0)
        text_obj = Text(midpoint, self.name)
        text_obj.setSize(7)
        text_obj.setRotation((math_utils.degrees_clockwise(self.dx, self.dy) % 180) - 90)
        return text_obj

    def draw(self, canvas):
        for line in self.lines:
            line.draw(canvas)

    def draw_text(self, canvas):
        self.text.undraw()
        self.text.draw(canvas)

    def undraw_text(self):
        self.text.undraw()

    def get_lane_adjusted_point(self, x, y, lane_num, reverse=False):
        if not reverse:
            new_point = Point(
                x - (self.way_gap * self.unit_y) - lane_num * (self.lane_gap * self.unit_y),
                y + (self.way_gap * self.unit_x) + lane_num * (self.lane_gap * self.unit_x)
            )
        else:
            new_point = Point(
                x + (self.way_gap * self.unit_y) + lane_num * (self.lane_gap * self.unit_y),
                y - (self.way_gap * self.unit_x) - lane_num * (self.lane_gap * self.unit_x)
            )
        return new_point

    def clicked(self, p):
        clicked_p0_dist = math_utils.distance(p, self.p0)
        clicked_p1_dist = math_utils.distance(p, self.p1)
        if clicked_p0_dist + clicked_p1_dist <= self.distance + self.click_threshold:
            return True
        return False

    def get_info(self):
        info = {
            "type": "Road",
            "id": self.id,
            "name": self.name,
            "lanes": self.lanes,
        }
        return info


class Road2W(Road):
    """graphical representation of two opposite edges - two way road"""
    def __init__(self, edge_id, p0, p1, name, lanes):
        super().__init__(edge_id, p0, p1, name, lanes)
        self.lanes = lanes
        self.lines = []
        self.way_gap = 5
        self.lane_gap /= 2

        for i in range(0, self.lanes, 2):
            u0 = self.get_lane_adjusted_point(p0.x, p0.y, i)
            u1 = self.get_lane_adjusted_point(p1.x, p1.y, i)
            w0 = self.get_lane_adjusted_point(p0.x, p0.y, i, reverse=True)
            w1 = self.get_lane_adjusted_point(p1.x, p1.y, i, reverse=True)
            self.lines.append(self.create_line(u0, u1, self.width))
            self.lines.append(self.create_line(w1, w0, self.width))


class Intersection:
    """graphical representation of a vertex"""
    def __init__(self, vertex):
        self.id = vertex.id
        self.x = vertex.x
        self.y = vertex.y
        self.radius = 3
        self.shape = Circle(Point(self.x, self.y), self.radius)

    def __repr__(self):
        return "Intersection {0}: ({1}, {2})".format(self.id, self.x, self.y)

    def draw(self, canvas):
        self.shape.draw(canvas)

    def clicked(self, p):
        xmin = self.x - self.radius
        xmax = self.x + self.radius
        ymin = self.y - self.radius
        ymax = self.y + self.radius
        return (xmin <= p.getX() <= xmax and ymin <= p.getY() <= ymax)

    def get_info(self):
        info = {
            "type": "Intersection",
            "id": self.id,
            "x": "{0:.1f}".format(self.x),
            "y": "{0:.1f}".format(self.y),
        }
        return info
