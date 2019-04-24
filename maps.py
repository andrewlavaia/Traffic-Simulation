import graphs
from graphics import Circle, Line, Point, color_rgb, Text
import math_utils


class RoadMap:
    """graphical representation of a graph"""
    def __init__(self, graph, canvas):
        self.canvas = canvas
        self.intersections = []
        self.roads = set()

        for vertex in graph.vertices.values():
            self.intersections.append(Intersection(vertex))
            for edge in vertex.getEdges():
                p0 = Point(graph.vertices[edge.source].x, graph.vertices[edge.source].y)
                p1 = Point(graph.vertices[edge.dest].x, graph.vertices[edge.dest].y)

                no_two_way_road_found = True
                for edge in graph.vertices[edge.dest].edges:
                    dest_point = Point(graph.vertices[edge.dest].x, graph.vertices[edge.dest].y)
                    if dest_point == p0:
                        no_two_way_road_found = False
                        if Road2W(p1, dest_point, edge.name) not in self.roads:
                            self.roads.add(Road2W(p0, p1, edge.name))

                if no_two_way_road_found:
                    self.roads.add(Road(p0, p1, edge.name))

    def getRoadsWithinView(self):
        x0, y1, x1, y0 = self.canvas.getCoords()
        x0 += self.canvas.canvasx(0)/self.canvas.zoom_factor
        x1 += self.canvas.canvasx(0)/self.canvas.zoom_factor
        y0 += self.canvas.canvasy(0)/self.canvas.zoom_factor
        y1 += self.canvas.canvasy(0)/self.canvas.zoom_factor

        roads_within_view = set()
        for road in self.roads:
            p0x = road.p0.x
            p0y = road.p0.y
            p1x = road.p1.x
            p1y = road.p1.y
            if ((x0 < road.p0.x < x1 and y0 < road.p0.y < y1) or
                    (x0 < road.p1.x < x1 and y0 < road.p1.y < y1)):
                roads_within_view.add(road.name)

        return roads_within_view

    def draw(self):
        for intersection in self.intersections:
            intersection.draw(self.canvas)

        road_names = {}
        for road in sorted(self.roads, key=lambda x: x.p0.x):
            road.draw(self.canvas)
            road_names[road.name] = road

        # draw street names separately so they are always on top
        # TODO separate function that needs to get called periodically on map moves and zooms?
        for road in road_names.values():
            road.drawText(self.canvas)


class Road:
    """graphical representation of a single edge - one way road"""
    def __init__(self, p0, p1, name):
        self.p0 = p0
        self.p1 = p1
        self.name = name
        self.dx = self.p1.x - self.p0.x
        self.dy = self.p1.y - self.p0.y
        self.width = 5

        self.line = self.createLine(self.p0, self.p1, self.width)
        self.text = self.createText()

    def __eq__(self, other):
        return self.p0 == other.p0 and self.p1 == other.p1

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
        self.line.draw(canvas)

    def drawText(self, canvas):
        self.text.draw(canvas)


class Road2W(Road):
    """graphical representation of two opposite edges - two way road"""
    def __init__(self, p0, p1, name):
        super().__init__(p0, p1, name)

        # get two parallel lines offset from original line,
        # going in opposite directions
        length = math_utils.pythag(self.dx, self.dy)
        unit_x = self.dx / length
        unit_y = self.dy / length
        gap = 5  # size of gap between lines

        self.u0 = Point(self.p0.x - gap * unit_y, self.p0.y + gap * unit_x)
        self.u1 = Point(self.p1.x - gap * unit_y, self.p1.y + gap * unit_x)
        self.w0 = Point(self.p0.x + gap * unit_y, self.p0.y - gap * unit_x)
        self.w1 = Point(self.p1.x + gap * unit_y, self.p1.y - gap * unit_x)

        self.line1 = self.createLine(self.u0, self.u1, self.width)
        self.line2 = self.createLine(self.w1, self.w0, self.width)

    def __eq__(self, other):
        return ((self.p0 == other.p0 and self.p1 == other.p1) or
                (self.p0 == other.p1 and other.p0 == self.p1))

    def __hash__(self):
        p0_tuple = (self.p0.x, self.p0.y)
        p1_tuple = (self.p1.x, self.p1.y)
        return hash(frozenset([p0_tuple, p1_tuple]))

    def draw(self, canvas):
        self.line1.draw(canvas)
        self.line2.draw(canvas)


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
