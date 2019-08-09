import graphs
from graphics import Circle, Line, Point, color_rgb, Text
import math_utils


class RoadMap:
    """graphical representation of a graph"""
    def __init__(self, graph, canvas):
        self.canvas = canvas
        self.intersections = {}   # vertex_id: Intersection
        self.roads = {}           # edge_id: Road
        self.route = frozenset()  # store selected car's current route

        for vertex in graph.vertices.values():
            self.intersections[vertex.id] = Intersection(vertex)
            for edge in vertex.getEdges():
                p0 = Point(graph.vertices[edge.source].x, graph.vertices[edge.source].y)
                p1 = Point(graph.vertices[edge.dest].x, graph.vertices[edge.dest].y)

                if edge.is_one_way:
                    self.roads[edge.id] = Road(edge.id, p0, p1, edge.name, edge.lanes)
                else:
                    self.roads[edge.id] = Road2W(edge.id, p0, p1, edge.name, edge.lanes)

    def getRoadsWithinView(self):
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

        self.drawRoadNames()  # drawn last so road names are on top

    def renderRoadNames(self):
        # don't redraw new road names every frame, just move the existing ones
        # until road is no longer in view?
        pass

    def drawRoadNames(self):
        road_names = {}
        roads_within_view = self.getRoadsWithinView()

        for road in roads_within_view:
            road_names[road.name] = road
            road.undrawText()
            road.drawText(self.canvas)

    def drawRoute(self, route, show_route):
        if not show_route:
            self.clearRoute(self.route)
            self.route = frozenset()
            return

        for vertex_id in route:
            intersection = self.intersections[vertex_id]
            intersection.shape.setFill("blue")

        old_route = self.route - set(route)
        self.clearRoute(old_route)
        self.route = frozenset(route)

    def clearRoute(self, route):
        for vertex_id in route:
            intersection = self.intersections[vertex_id]
            intersection.shape.setFill("")

    def showInfo(self, map_object):
        print(map_object)
        # TODO implement an on-screen display or pop-up window for this


class Road:
    """graphical representation of a single edge - one way road"""
    def __init__(self, edge_id, p0, p1, name, lanes):
        self.id = edge_id
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
        # This is only used for quickly creating a set of roads by name
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "Road {0}: {1} ({2}, {3}) - ({4}, {5})".format(
            self.id, self.name, self.p0.x, self.p0.y, self.p1.x, self.p1.y
        )

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
    def __init__(self, edge_id, p0, p1, name, lanes):
        super().__init__(edge_id, p0, p1, name, lanes)
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
        # This is only used for quickly creating a set of roads by name
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

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
