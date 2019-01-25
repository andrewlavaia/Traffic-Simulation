from graphics import Point, Polygon
import math_utils


class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 1
        self.width = 5
        self.height = 15
        self.direction = 0
        self.source = None
        self.dest = None

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

    def render(self, canvas):
        pass

    def move(self, dx, dy):
        self.shape.move(dx, dy)

    def rotate(self, dx, dy):
        # new_direction = math_utils.degrees_clockwise(dx, dy)
        # degrees_counterclockwise = self.direction - new_direction
        self.shape.rotate(1)
