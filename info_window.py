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
            self.flip_show_route,
            self.canvas,
            Point(self.canvas.width/2, 375),
            300,
            50,
            'Show Route'
        )
        self.follow_btn = Button(
            self.flip_follow_car,
            self.canvas,
            Point(self.canvas.width/2, 450),
            300,
            50,
            'Follow Selected Car'
        )
        self.buttons = [self.show_route_btn, self.follow_btn]

    def set_selected_car(self, car):
        self.selected_car = car

    def flip_show_route(self):
        self.show_route = not self.show_route

    def flip_follow_car(self):
        self.follow_car = not self.follow_car

    def initialize_table(self):
        for label, value in self.selected_car.get_info().items():
            self.table.add_row(label, value)

    def updateTable(self):
        info = self.selected_car.get_info()
        rows = []
        for key, value in info.items():
            rows.append(TableRow(self.canvas, (key, value)))
        self.table.update_rows(rows)
