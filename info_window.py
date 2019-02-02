from ui import HeaderText, Table
from graphics import Point


class InfoWindow:
    def __init__(self, canvas):
        self.canvas = canvas
        self.table = Table(self.canvas, Point(50, 25))

    def updateTable(self, info):
        self.table.deleteAllRows()
        for label, value in info.items():
            self.table.addRow(label, value)
