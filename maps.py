import graphs
from graphics import Circle, Line, Point, color_rgb


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
                for road in self.roads:
                    # check for two way road
                    if road.p0 == p1 and road.p1 == p0:
                        # remove existing road and replace with two way road?
                        pass
                self.roads.append(Road(p0, p1))

    def draw(self):
        for intersection in self.intersections:
            intersection.draw(self.canvas)

        for road in self.roads:
            road.draw(self.canvas)


class Road:
    """graphical representation of an edge"""
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        self.line = Line(self.p0, self.p1)
        self.line.setWidth(6)
        color = color_rgb(200, 200, 200)
        self.line.setOutline(color)
        self.line.setArrow("last")

    def draw(self, canvas):
        self.line.draw(canvas)


class Intersection:
    """graphical representation of a vertex"""
    def __init__(self, vertex):
        self.id = vertex.id
        self.x = vertex.x
        self.y = vertex.y
        self.radius = 10
        self.shape = Circle(Point(self.x, self.y), self.radius)

    def draw(self, canvas):
        self.shape.draw(canvas)


class MapCreator:
    """create a random map from a given number of vertices and edges"""
    pass
