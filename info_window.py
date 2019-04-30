from ui import HeaderText, Table, Button
from graphics import Point


class InfoWindow:
    def __init__(self, canvas):
        self.canvas = canvas
        self.table = Table(self.canvas, Point(100, 25), col_width=150)
        self.selected_car = None
        self.show_route = False
        self.follow_car = False
        self.show_route_btn = Button(
            self.showRoute,
            self.canvas,
            Point(self.canvas.width/2, 300),
            300,
            50,
            'Show Route'
        )
        self.follow_btn = Button(
            self.followCar,
            self.canvas,
            Point(self.canvas.width/2, 400),
            300,
            50,
            'Follow Selected Car'
        )
        self.buttons = [self.show_route_btn, self.follow_btn]

    def setSelectedCar(self, car):
        if self.selected_car is not None:
            self.selected_car.shape.setFill("white")
        self.selected_car = car
        self.selected_car.shape.setFill("yellow")

    def showRoute(self):
        self.show_route = not self.show_route

    def followCar(self):
        self.follow_car = not self.follow_car

    def updateTable(self):
        try:
            self.table.deleteAllRows()
            for label, value in self.selected_car.getInfo().items():
                self.table.addRow(label, value)
        except AttributeError:  # self.selected_car is None
            pass
