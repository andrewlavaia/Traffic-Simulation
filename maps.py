import graphs
from graphics import Circle, Line, Point, color_rgb, Text
import math_utils


class RoadMap:
    """graphical representation of a graph"""
    def __init__(self, graph, canvas):
        self.canvas = canvas
        self.intersections = {}
        self.roads = set()

        for vertex in graph.vertices.values():
            self.intersections[vertex.id] = Intersection(vertex)
            for edge in vertex.getEdges():
                p0 = Point(graph.vertices[edge.source].x, graph.vertices[edge.source].y)
                p1 = Point(graph.vertices[edge.dest].x, graph.vertices[edge.dest].y)

                no_two_way_road_found = True
                for edge in graph.vertices[edge.dest].edges:
                    dest_point = Point(graph.vertices[edge.dest].x, graph.vertices[edge.dest].y)
                    if dest_point == p0:
                        no_two_way_road_found = False
                        if Road2W(p1, dest_point, edge.name, edge.lanes) not in self.roads:
                            self.roads.add(Road2W(p0, p1, edge.name, edge.lanes))

                if no_two_way_road_found:
                    self.roads.add(Road(p0, p1, edge.name, edge.lanes))

    def getRoadsWithinView(self):
        x0, y1, x1, y0 = self.canvas.getCanvasCoords()
        roads_within_view = set()
        for road in self.roads:
            if ((x0 < road.p0.x < x1 and y0 < road.p0.y < y1) or
                    (x0 < road.p1.x < x1 and y0 < road.p1.y < y1)):
                roads_within_view.add(road)

        return roads_within_view

    def draw(self):
        for intersection in self.intersections.values():
            intersection.draw(self.canvas)

        for road in self.roads:
            road.draw(self.canvas)

        self.drawRoadNames()  # drawn last so road names are on top

    def drawRoadNames(self):
        road_names = {}
        roads_within_view = self.getRoadsWithinView()

        for road in self.roads:
            if road in roads_within_view:
                road_names[road.name] = road
            road.undrawText()

        for road in road_names.values():
            road.drawText(self.canvas)

    def drawRoute(self, route, show_route):
        for vertex_id, intersection in self.intersections.items():
            if show_route and vertex_id in route:
                intersection.shape.setFill("blue")
            else:
                intersection.shape.setFill("")


class Road:
    """graphical representation of a single edge - one way road"""
    def __init__(self, p0, p1, name, lanes):
        self.id = id(self)
        self.p0 = p0
        self.p1 = p1
        self.name = name
        self.lanes = lanes

        self.dx = self.p1.x - self.p0.x
        self.dy = self.p1.y - self.p0.y
        self.length = math_utils.pythag(self.dx, self.dy)
        self.unit_x = self.dx / self.length
        self.unit_y = self.dy / self.length

        self.lines = []
        self.width = 2
        self.way_gap = 0  # size of gap between each road direction
        self.lane_gap = 4  # size of gap between lines

        for i in range(lanes):
            u0 = self.getLaneAdjustedPoint(self.p0, i)
            u1 = self.getLaneAdjustedPoint(self.p1, i)
            self.lines.append(self.createLine(u0, u1, self.width))
        self.text = self.createText()

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        p0_tuple = (self.p0.x, self.p0.y)
        p1_tuple = (self.p1.x, self.p1.y)
        return hash((p0_tuple, p1_tuple))

    @staticmethod
    def createLine(p0, p1, width):
        line = Line(p0, p1)
        line.setWidth(width)
        color = color_rgb(200, 200, 200)
        line.setOutline(color)
        line.setArrow("last")
        return line

    def createText(self):
        midpoint = Point((self.p0.x + self.p1.x)/2.0, (self.p0.y + self.p1.y)/2.0)
        text_obj = Text(midpoint, self.name)
        text_obj.setSize(8)
        text_obj.setRotation((math_utils.degrees_clockwise(self.dx, self.dy) % 180) - 90)
        return text_obj

    def draw(self, canvas):
        for line in self.lines:
            line.draw(canvas)

    def drawText(self, canvas):
        self.text.undraw()
        self.text.draw(canvas)

    def undrawText(self):
        self.text.undraw()

    def getLaneAdjustedPoint(self, p0, lane_num, reverse=False):
        if not reverse:
            new_point = Point(
                p0.x - (self.way_gap * self.unit_y) - lane_num * (self.lane_gap * self.unit_y),
                p0.y + (self.way_gap * self.unit_x) + lane_num * (self.lane_gap * self.unit_x)
            )
        else:
            new_point = Point(
                p0.x + (self.way_gap * self.unit_y) + lane_num * (self.lane_gap * self.unit_y),
                p0.y - (self.way_gap * self.unit_x) - lane_num * (self.lane_gap * self.unit_x)
            )
        return new_point


class Road2W(Road):
    """graphical representation of two opposite edges - two way road"""
    def __init__(self, p0, p1, name, lanes):
        super().__init__(p0, p1, name, lanes)
        self.lanes = lanes
        self.lines = []
        self.way_gap = 5
        self.lane_gap /= 2

        for i in range(0, self.lanes, 2):
            u0 = self.getLaneAdjustedPoint(p0, i)
            u1 = self.getLaneAdjustedPoint(p1, i)
            w0 = self.getLaneAdjustedPoint(p0, i, reverse=True)
            w1 = self.getLaneAdjustedPoint(p1, i, reverse=True)
            self.lines.append(self.createLine(u0, u1, self.width))
            self.lines.append(self.createLine(w1, w0, self.width))

    def __eq__(self, other):
        return ((self.p0 == other.p0 and self.p1 == other.p1) or
                (self.p0 == other.p1 and other.p0 == self.p1))

    def __hash__(self):
        p0_tuple = (self.p0.x, self.p0.y)
        p1_tuple = (self.p1.x, self.p1.y)
        return hash(frozenset([p0_tuple, p1_tuple]))

    def draw(self, canvas):
        for line in self.lines:
            line.draw(canvas)


class Intersection:
    """graphical representation of a vertex"""
    def __init__(self, vertex):
        self.id = vertex.id
        self.x = vertex.x
        self.y = vertex.y
        self.radius = 3
        self.shape = Circle(Point(self.x, self.y), self.radius)

    def draw(self, canvas):
        self.shape.draw(canvas)
