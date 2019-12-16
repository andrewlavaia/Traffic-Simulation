from file_utils import csv_to_dict, load_yaml
from graphics import Point
from ui import Button, HeaderText, InputBox, Table


class MainMenu:
    def __init__(self, window, callback, config="config.yml", secondary_window=None):
        self.window = window
        self.callback = callback
        self.config_data = load_yaml(config)
        self.secondary_window = secondary_window

        self.buttons = []
        self.inputs = []
        self.labels = []

        simulation_btn = Button(
            self.callback, self.window, Point(700, 300), 200, 100, 'Run Simulation'
        )
        self.buttons.append(simulation_btn)

        margin_top = 50
        length = 6
        input_box_width = 80
        x = 250
        y = 100
        font_size = 12

        map_coords_header = HeaderText(self.window, Point(x, y), 'Map Coordinates')
        self.labels.append(map_coords_header)

        y += margin_top
        self.input_n = InputBox(
            self.window, Point(x, y), 'float', 'Latitude North: ', length, input_box_width
        )
        self.inputs.append(self.input_n)
        y += margin_top
        self.input_w = InputBox(
            self.window, Point(x, y), 'float', 'Longitude West: ', length, input_box_width
        )
        self.inputs.append(self.input_w)
        y += margin_top
        self.input_s = InputBox(
            self.window, Point(x, y), 'float', 'Latitude South: ', length, input_box_width
        )
        self.inputs.append(self.input_s)
        y += margin_top
        self.input_e = InputBox(
            self.window, Point(x, y), 'float', 'Longitude East: ', length, input_box_width
        )
        self.inputs.append(self.input_e)

        y += margin_top
        divider_text = "-" * 30
        divider = HeaderText(self.window, Point(x, y), divider_text, font_size=font_size)
        self.labels.append(divider)

        y += margin_top
        self.input_zip_code = InputBox(
            self.window, Point(x, y), 'unsigned_int', 'Zip Code: ', length, input_box_width
        )
        self.inputs.append(self.input_zip_code)

        y += margin_top
        populate_coords = Button(
            self.populate_coords_from_zip, self.window, Point(x, y),
            350, 30, 'Populate Coordinates from Zip Code (US only)', font_size=font_size
        )
        self.buttons.append(populate_coords)

        y += margin_top
        divider_text = "-" * 100
        divider = HeaderText(self.window, Point(x, y), divider_text, font_size=font_size)

    @property
    def us_zip_code_data(self):
        filename = "us_zip_codes.csv"
        return csv_to_dict(filename)

    def draw_menu(self):
        self.window.clear()
        self.window.setBackground('white')
        self.window.resetView()

        if self.secondary_window:
            self.secondary_window.forget()

        elements = self.buttons + self.inputs + self.labels
        for element in elements:
            element.draw()

    def run(self):
        self.draw_menu()

        while True:
            last_clicked_pt = self.window.getMouse()
            if last_clicked_pt is not None and self.valid_inputs:
                for button in self.buttons:
                    button.clicked(last_clicked_pt)

    def valid_inputs(self):
        result = True
        for input_box in self.inputs:
            result |= input_box.validate_input()
        return result

    def populate_coords_from_zip(self):
        pass
