from ui import HeaderText, Table, TableRow, Button
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
            Point(self.canvas.width/2, 375),
            300,
            50,
            'Show Route'
        )
        self.follow_btn = Button(
            self.followCar,
            self.canvas,
            Point(self.canvas.width/2, 450),
            300,
            50,
            'Follow Selected Car'
        )
        self.buttons = [self.show_route_btn, self.follow_btn]

    def setSelectedCar(self, car):
        self.selected_car = car

    def showRoute(self):
        self.show_route = not self.show_route

    def followCar(self):
        self.follow_car = not self.follow_car

    def initializeTable(self):
        for label, value in self.selected_car.getInfo().items():
            self.table.addRow(label, value)

    def updateTable(self):
        info = self.selected_car.getInfo()
        rows = []
        for key, value in info.items():
            rows.append(TableRow(self.canvas, (key, value)))
        self.table.updateRows(rows)
