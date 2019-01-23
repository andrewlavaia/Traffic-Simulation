import graphs
from graphics import Circle, Line, Point, color_rgb
import math_utils


class RoadMap:
    """graphical representation of a graph"""
    def __init__(self, graph, canvas):
        self.canvas = canvas
        self.intersections = []
        self.roads = []

        for vertex in graph.vertices.values():
            self.intersections.append(Intersection(vertex))
            for edge in vertex.getEdges():
                p0 = Point(graph.vertices[edge.source].x, graph.vertices[edge.source].y)
                p1 = Point(graph.vertices[edge.dest].x, graph.vertices[edge.dest].y)

                # replace roads with sub-types
                no_subtype_needed = True
                for road in self.roads:
                    if road.p0 == p1 and road.p1 == p0:
                        no_subtype_needed = False
                        self.roads.remove(road)
                        self.roads.append(Road2W(p0, p1))

                if no_subtype_needed:
                    self.roads.append(Road(p0, p1))

    def draw(self):
        for intersection in self.intersections:
            intersection.draw(self.canvas)

        for road in self.roads:
            road.draw(self.canvas)


class Road:
    """graphical representation of a single edge - one way road"""
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        self.dx = self.p1.x - self.p0.x
        self.dy = self.p1.y - self.p0.y
        self.width = 5

        self.line = self.createLine(self.p0, self.p1, self.width)

    @staticmethod
    def createLine(p0, p1, width):
        line = Line(p0, p1)
        line.setWidth(width)
        color = color_rgb(200, 200, 200)
        line.setOutline(color)
        line.setArrow("last")
        return line

    def draw(self, canvas):
        self.line.draw(canvas)


class Road2W(Road):
    """graphical representation of two opposite edges - two way road"""
    def __init__(self, p0, p1):
        super().__init__(p0, p1)

        # get two parallel lines offset from original line,
        # going in opposite directions
        length = math_utils.pythag(self.dx, self.dy)
        unit_x = abs(self.dx / length)
        unit_y = abs(self.dy / length)
        gap = 5  # size of gap between lines

        self.u0 = Point(self.p0.x - gap * unit_y, self.p0.y - gap * unit_x)
        self.u1 = Point(self.p1.x - gap * unit_y, self.p1.y - gap * unit_x)
        self.w0 = Point(self.p0.x + gap * unit_y, self.p0.y + gap * unit_x)
        self.w1 = Point(self.p1.x + gap * unit_y, self.p1.y + gap * unit_x)

        # enforce right lane driving
        if self.dx <= 0:
            self.line1 = self.createLine(self.u0, self.u1, self.width)
            self.line2 = self.createLine(self.w1, self.w0, self.width)
        else:
            self.line1 = self.createLine(self.u1, self.u0, self.width)
            self.line2 = self.createLine(self.w0, self.w1, self.width)

    def draw(self, canvas):
        self.line1.draw(canvas)
        self.line2.draw(canvas)


class Intersection:
    """graphical representation of a vertex"""
    def __init__(self, vertex):
        self.id = vertex.id
        self.x = vertex.x
        self.y = vertex.y
        self.radius = 15
        self.shape = Circle(Point(self.x, self.y), self.radius)

    def draw(self, canvas):
        self.shape.draw(canvas)


class MapCreator:
    """create a random map from a given number of vertices and edges"""
    pass
