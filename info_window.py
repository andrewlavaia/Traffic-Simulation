from ui import HeaderText, Table, Button
from graphics import Point


class InfoWindow:
    def __init__(self, canvas, road_map):
        self.canvas = canvas
        self.road_map = road_map
        self.table = Table(self.canvas, Point(50, 25))
        self.selected_car = None
        self.show_route_btn = Button(
            getattr(self, "showRoute"),
            self.canvas,
            Point(self.canvas.width/2, 300),
            300,
            50,
            'Show Route'
        )
        self.follow_btn = Button(
            getattr(self, "followCar"),
            self.canvas,
            Point(self.canvas.width/2, 400),
            300,
            50,
            'Follow Selected Car'
        )

    def setSelectedCar(self, car):
        if self.selected_car is not None:
            self.selected_car.shape.setFill("white")
        self.selected_car = car
        self.selected_car.shape.setFill("yellow")

    def showRoute(self):
        self.road_map.drawCarRoute(self.selected_car)

    def followCar(self):
        pass

    def updateTable(self):
        try:
            self.table.deleteAllRows()
            for label, value in self.selected_car.getInfo().items():
                self.table.addRow(label, value)
        except AttributeError:  # self.selected_car is None
            pass
