import random

from graphics import Point, Polygon, Rectangle
import math_utils
from graphs import ShortestPaths


class Car:
    def __init__(self, graph, source):
        self.id = id(self)
        self.graph = graph
        self.source = source
        self.x = source.x
        self.y = source.y
        self.speed = 20
        self.width = 5
        self.height = 15
        self.direction = 0
        self.shortest_paths = ShortestPaths(graph, source)
        self.dest_id = self.chooseDest()
        self.route = self.getShortestPathToDest()
        self.next_dest = self.getNextDest()
        print("Car {0} moving from {1} to {2}".format(self.id, self.source.id, self.dest_id))

        # car shape must be a polygon because rectangles are represented as two points
        # which prevents proper rotations and translations
        center = Point(self.x, self.y)
        p1 = Point(self.x - (self.width/2), self.y - (self.height/2))
        p2 = Point(self.x + (self.width/2), self.y - (self.height/2))
        p3 = Point(self.x + (self.width/2), self.y + (self.height/2))
        p4 = Point(self.x - (self.width/2), self.y + (self.height/2))
        points = [p1, p2, p3, p4]
        self.shape = Polygon(center, points)

    def draw(self, canvas):
        self.shape.draw(canvas)

    def rotate(self, dx, dy):
        if dx == 0 and dy == 0:
            return
        new_direction = math_utils.degrees_clockwise(dx, dy)
        degrees = float(self.direction - new_direction)
        self.shape.rotate(degrees)
        self.direction = new_direction

    def render(self, canvas):
        dx = self.x - self.shape.center.x
        dy = self.y - self.shape.center.y
        self.rotate(dx, dy)
        self.shape.move(dx, dy)

    def moveTowardsDest(self, dt):
        movement = (dt * self.speed)
        dx = self.next_dest.x - self.x
        dy = self.next_dest.y - self.y

        if abs(dx) <= movement and abs(dy) <= movement:
            self.next_dest = self.getNextDest()
            return

        dist = math_utils.pythag(dx, dy)
        mv_x = (dx/dist) * movement
        mv_y = (dy/dist) * movement

        self.x += mv_x
        self.y += mv_y

    def chooseDest(self):
        vertices = list(self.graph.vertices.keys())
        vertices.remove(self.source.id)
        return random.choice(vertices)

    def getShortestPathToDest(self):
        route = []
        dest = self.dest_id
        while (dest != self.source.id):
            edge = self.shortest_paths.path_of_edges[dest]
            dest = edge.source
            route.append(dest)
        return route

    def getNextDest(self):
        if not self.route:
            self.source = self.graph.vertices[self.dest_id]
            self.dest_id = self.chooseDest()
            self.shortest_paths = ShortestPaths(self.graph, self.source)
            self.route = self.getShortestPathToDest()
            print("Car {0} moving from {1} to {2}".format(self.id, self.source.id, self.dest_id))

        dest_id = self.route.pop()
        return self.graph.vertices[dest_id]
