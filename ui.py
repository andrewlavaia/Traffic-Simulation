import re
from abc import ABCMeta, abstractmethod
from graphics import Entry, Point, Rectangle, Text


class UIBase(metaclass=ABCMeta):
    @abstractmethod
    def draw(self):
        """Draws object on self.canvas"""

    @abstractmethod
    def undraw(self):
        """Removes object from self.canvas"""

    def redraw(self):
        self.undraw()
        self.draw()


class Button(UIBase):
    def __init__(
        self, callback, canvas, center, width=100, height=100, label="Button", font_size=14
    ):
        """Creates a button that fires a callback when clicked"""
        self.callback = callback
        self.canvas = canvas
        w, h = width/2.0, height/2.0
        x, y = center.getX(), center.getY()
        self.xmax, self.xmin = x+w, x-w
        self.ymax, self.ymin = y+h, y-h
        p1 = Point(self.xmin, self.ymin)
        p2 = Point(self.xmax, self.ymax)
        self.rect = Rectangle(p1, p2)
        self.rect.setFill('lightgray')
        self.label = Text(center, label)
        self.label.setSize(font_size)
        self.draw()
        self.activate()

    def clicked(self, p):
        """Fires callback if active p is inside"""
        if (self.active and
                self.xmin <= p.getX() <= self.xmax and
                self.ymin <= p.getY() <= self.ymax):
            return self.callback()

    def get_label(self):
        return self.label.getText()

    def activate(self):
        self.label.setFill('black')
        self.rect.setWidth(2)
        self.active = 1

    def deactivate(self):
        self.label.setFill('darkgrey')
        self.rect.setWidth(1)
        self.active = 0

    def draw(self):
        self.rect.draw(self.canvas)
        self.label.draw(self.canvas)

    def undraw(self):
        self.rect.undraw()
        self.label.undraw()


class InputBox(UIBase):
    def __init__(self, canvas, point, input_type, label_text, char_max=10, default_val=None):
        allowed_types = ['unsigned_int', 'unsigned_float', 'float']
        if input_type not in allowed_types:
            raise Exception('InputBox: type given is not an allowed type')

        self.canvas = canvas
        self.point = point
        self.type = input_type
        self.label = Text(point, label_text)
        x_offset = 120 + ((char_max - 10)/2.0 * 9)  # diff b/t default char_max and font_size / 2
        self.entry = Entry(Point(point.x + x_offset, point.y), char_max)
        if default_val is not None:
            self.set_input(default_val)
        self.draw()

    @property
    def input_text(self):
        return self.entry.getText()

    def validate_input(self):
        flag = True
        if self.type == 'unsigned_int':
            flag = isinstance(int(self.input_text), int) and int(self.input_text) > 0
        elif self.type == 'unsigned_float':
            flag = isinstance(float(self.input_text), float) and float(self.input_text) > 0
        elif self.type == 'float':
            flag = isinstance(float(self.input_text), float)

        if not flag:
            self.label.setTextColor('red')
        else:
            self.label.setTextColor('black')
        return flag

    def set_input(self, val):
        self.entry.setText(val)
        if self.validate_input() is not True:
            self.entry.setText('')

    def draw(self):
        self.label.draw(self.canvas)
        self.entry.draw(self.canvas)

    def undraw(self):
        self.label.undraw()
        self.entry.undraw()

    def get_point_with_offset(self):
        return Point(self.point.x, self.point.y + 30)


class Table(UIBase):
    def __init__(self, canvas, point, row_height=30, col_width=120, font_size=12):
        self.canvas = canvas
        self.point = point
        self.rows = []
        self.row_height = row_height
        self.col_width = col_width
        self.font_size = font_size

    def add_row(self, *args):
        row = TableRow(self.canvas, args)
        self.rows.append(row)
        self.redraw()

    def delete_row(self, row_id):
        for row in self.rows:
            if row.values[0] == row_id:
                row.undraw()
                self.rows.remove(row)
        self.redraw()

    def delete_all_rows(self):
        for row in self.rows:
            row.undraw()
        self.rows = []

    def update_rows(self, new_rows):
        for i, row in enumerate(self.rows):
            if row != new_rows[i]:
                self.rows[i].undraw()
                self.rows[i] = new_rows[i]
                y = self.point.y + (i * self.row_height)
                self.rows[i].create_labels(
                    self.point.x, y, self.col_width, font_size=self.font_size
                )
                self.rows[i].draw()

    def draw(self):
        for i, row in enumerate(self.rows):
            y = self.point.y + (i * self.row_height)
            row.create_labels(self.point.x, y, self.col_width, font_size=self.font_size)
            row.draw()

    def undraw(self):
        for row in self.rows:
            row.undraw()


class TableRow(UIBase):
    def __init__(self, canvas, *args):
        self.canvas = canvas
        self.values = list(*args)
        self.labels = []
        self.button = None

    def __eq__(self, other):
        return tuple(self.values) == tuple(other.values)

    def __repr__(self):
        return str(self.values)

    def create_labels(self, x, y, col_width, alignment="right", font_size=10):
        for i, value in enumerate(self.values):
            x += i * col_width
            label = Text(Point(x, y), value)
            label.setSize(font_size)
            label.setAlignment(alignment)
            self.labels.append(label)

    def draw(self):
        for label in self.labels:
            label.draw(self.canvas)

    def undraw(self):
        for label in self.labels:
            label.undraw()
        if self.button:
            self.button.deactivate()
            self.button.undraw()
        self.labels.clear()
        self.button = None


class HeaderText(UIBase):
    def __init__(self, canvas, point, text, font_size=24, style="normal", align="left"):
        self.canvas = canvas
        self.text = Text(point, text)
        self.text.setSize(font_size)
        self.text.setStyle(style)
        self.text.setAlignment(align)
        self.draw()

    def draw(self):
        self.text.draw(self.canvas)

    def undraw(self):
        self.text.undraw()
