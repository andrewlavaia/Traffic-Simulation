import functools

from graphics import Point, Polygon
import math_utils


class Car:
    def __init__(self, index, gps, source_id):
        self.index = index
        self.id = id(self)
        self.gps = gps
        self.source_id = source_id
        self.dest_id = source_id
        self.x, self.y = self.gps.getCoordinates(source_id)
        self.speed = 20.0
        self.speed_limit = 30.0
        self.width = 5
        self.height = 15
        self.direction = 0
        self.lane_index = 0
        self.source_id, self.dest_id, self.route = self.newRoute()
        self.next_dest_id = self.getNextDest()
        self.current_edge = self.gps.getEdge(self.source_id, self.next_dest_id)
        self.cell = None  # used in collision system
        # print("Car {0} moving from {1} to {2}".format(self.id, self.source_id, self.dest_id))

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    # @functools.lru_cache(maxsize=4)
    def checkCollision(self, other):
        """Check whether this car is about to smash into another car"""

        # Only check for forward collisions by checking movement vector
        adjustment_factor = 20.0
        nx, ny = self.gps.getLaneAdjCoords(self.next_dest_id, self.current_edge, self.lane_index)
        dx = nx - self.x
        dy = ny - self.y
        dist = math_utils.pythag(dx, dy) or 1.0
        mv_x = (dx/dist) * adjustment_factor
        mv_y = (dy/dist) * adjustment_factor

        # width vs height is dependent on the car's orientation,
        # simplify by always checking longest one
        x_overlap = (abs(self.x + mv_x - other.x) * 2) < (self.height + other.height)
        y_overlap = (abs(self.y + mv_y - other.y) * 2) < (self.height + other.height)
        collision_detected = x_overlap and y_overlap
        return collision_detected

    def throttleDown(self):
        min_speed = 3.0
        self.speed = max(self.speed * 0.9, min_speed)

    def throttleUp(self):
        self.speed *= 1.1
        if self.speed > self.speed_limit:
            self.speed = self.speed_limit

    def moveTowardsDest(self, dt):
        movement = (dt * self.speed)
        nx, ny = self.gps.getLaneAdjCoords(self.next_dest_id, self.current_edge, self.lane_index)
        dx = nx - self.x
        dy = ny - self.y
        dist = math_utils.pythag(dx, dy)

        if dist <= movement:
            new_source = self.next_dest_id
            self.next_dest_id = self.getNextDest()
            self.current_edge = self.gps.getEdge(new_source, self.next_dest_id)
            self.speed_limit = self.getSpeedLimit()
            return

        mv_x = (dx/dist) * movement
        mv_y = (dy/dist) * movement

        self.x += mv_x
        self.y += mv_y

    def chooseDest(self):
        return self.gps.randomVertex()

    def newRoute(self):
        new_source_id = self.dest_id
        new_dest_id = self.chooseDest()
        new_route = self.gps.shortestRoute(new_source_id, new_dest_id)
        new_route_count = 1
        while new_route is None and new_route_count < 10:
            new_dest_id = self.chooseDest()
            new_route = self.gps.shortestRoute(new_source_id, new_dest_id)
            new_route_count += 1

        if new_route is None:
            # Car reached a dead end. Seriously, why do one way dead ends with no exit even exist?
            # TODO -> systematically remove these from the map data when a car hits one?
            # print("Car {0} reached a dead end at {1}".format(self.id, new_source_id))
            self.resetCurrentLocation()
            return self.newRoute()

        # print("Car {0} moving from {1} to {2}".format(self.id, new_source_id, new_dest_id))
        return new_source_id, new_dest_id, new_route

    def getNextDest(self):
        if not self.route:
            self.source_id, self.dest_id, self.route = self.newRoute()
        dest_id = self.route.pop()
        return dest_id

    def getSpeedLimit(self):
        if self.current_edge and self.current_edge.speed_limit is not None:
            return float(self.current_edge.speed_limit)
        else:
            return self.speed_limit

    def resetCurrentLocation(self):
        """instantly transports car to a new random location"""
        self.source_id = self.gps.randomVertex()
        self.dest_id = self.source_id
        self.x, self.y = self.gps.getCoordinates(self.source_id)

    def getInfo(self):
        road_name = ""
        speed_limit = ""
        lanes = ""
        one_way = ""

        if self.current_edge:
            road_name = self.current_edge.name
            speed_limit = self.current_edge.speed_limit
            lanes = self.current_edge.lanes
            one_way = self.current_edge.is_one_way

        info = {
            "id": self.id,
            "x": "{0:.1f}".format(self.x),
            "y": "{0:.1f}".format(self.y),
            "source": self.source_id,
            "destination": self.dest_id,
            "speed": "{0:.2f}".format(self.speed),
            " ": "",
            "road name": road_name,
            "speed limit": speed_limit,
            "lanes": lanes,
            "one way": one_way,
        }
        return info


class CarShape():
    """Defines a shape object to be used for drawing the corresponding
    Car object with the same index"""
    def __init__(self, index, window, car):
        self.index = index
        self.window = window
        self.x = car.x
        self.y = car.y
        self.color = "white"
        self.height = car.height
        self.width = car.width
        self.direction = 0

        # car shape must be a polygon because rectangles are represented as two points
        # which prevents proper rotations and translations
        center = Point(self.x, self.y)
        p1 = (self.x - (self.width/2), self.y - (self.height/2))
        p2 = (self.x + (self.width/2), self.y - (self.height/2))
        p3 = (self.x + (self.width/2), self.y + (self.height/2))
        p4 = (self.x - (self.width/2), self.y + (self.height/2))
        points = [p1, p2, p3, p4]
        self.shape = Polygon(center, points)
        self.shape.setFill(self.color)

    def draw(self):
        self.shape.draw(self.window)

    def render(self):
        dx = self.x - self.shape.center.x
        dy = self.y - self.shape.center.y
        self.rotate(dx, dy)
        self.shape.move(dx, dy)

    def rotate(self, dx, dy):
        if dx == 0 and dy == 0:
            return
        new_direction = math_utils.degrees_clockwise(dx, dy)
        degrees = float(self.direction - new_direction)
        if abs(degrees) > 5:
            self.shape.rotate(degrees)
        self.direction = new_direction

    def clicked(self, p):
        x_points = [point[0] for point in self.shape.points]
        y_points = [point[1] for point in self.shape.points]
        xmin = min(x_points)
        xmax = max(x_points)
        ymin = min(y_points)
        ymax = max(y_points)
        return (xmin <= p.getX() <= xmax and ymin <= p.getY() <= ymax)


class CarFactory:
    """Used to create a Car with an associated CarShape"""
    def __init__(self, window, gps, cars, car_shapes):
        self.window = window
        self.gps = gps
        self.cars = cars
        self.car_shapes = car_shapes
        self.count = 0

    def create(self):
        index = self.count
        car = Car(index, self.gps, self.gps.randomVertex())
        self.cars.append(Car(index, self.gps, self.gps.randomVertex()))
        self.car_shapes.append(CarShape(index, self.window, self.cars[index]))
        self.count += 1
