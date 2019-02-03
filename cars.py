from graphics import Point, Polygon
import math_utils


class Car:
    def __init__(self, gps, source):
        self.id = id(self)
        self.gps = gps
        self.source = source
        self.dest = self.chooseDest()
        self.x = source.x
        self.y = source.y
        self.speed = 20.0
        self.width = 5
        self.height = 15
        self.direction = 0
        self.route = self.gps.shortestRoute(self.source, self.dest)
        self.next_dest = self.getNextDest()
        print("Car {0} moving from {1} to {2}".format(self.id, self.source.id, self.dest.id))

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
        dist = math_utils.pythag(dx, dy)

        if dist <= movement:
            self.next_dest = self.getNextDest()
            return

        mv_x = (dx/dist) * movement
        mv_y = (dy/dist) * movement

        self.x += mv_x
        self.y += mv_y

    def chooseDest(self):
        return self.gps.randomVertex()

    def newRoute(self):
        self.source = self.gps.getVertex(self.dest.id)
        self.dest = self.chooseDest()
        self.route = self.gps.shortestRoute(self.source, self.dest)
        print("Car {0} moving from {1} to {2}".format(self.id, self.source.id, self.dest.id))

    def getNextDest(self):
        if not self.route:
            self.newRoute()
        dest_id = self.route.pop()
        return self.gps.getVertex(dest_id)

    def getInfo(self):
        info = {
            "id": self.id,
            "source": self.source.id,
            "dest": self.dest.id,
            "speed": self.speed,
            "route": self.route,
        }
        return info
