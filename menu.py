from functools import lru_cache
import os

from file_utils import csv_to_dict, load_yaml, save_yaml
from graphics import Point
from openstreetmap import query_roads_by_lat_lon, save_raw_json_map_data
from ui import Button, HeaderText, InputBox, Table


MAP_DATA_DIR = "map_data"


class MainMenu:
    def __init__(self, window, callback, config="config_default.yml", hidden_windows=None):
        self.window = window
        self.callback = callback
        self.config_data = load_yaml(config)
        self.hidden_windows = hidden_windows or []

        self.buttons = []
        self.inputs = []
        self.labels = []

        self.simulation_btn = Button(
            self.simulation_btn_click, self.window, Point(640, 650), 600, 150, 'Run Simulation'
        )
        self.buttons.append(self.simulation_btn)

        font_size = 12
        length = 10
        margin_top = 50

        # Map Coordinates Section
        x = 250
        y = 100
        map_coords_header = HeaderText(self.window, Point(x, y), 'Map Coordinates', align="center")
        self.labels.append(map_coords_header)

        north = self.config_data["map_data"]["coords_north"]
        y += margin_top + 10
        self.input_n = InputBox(
            self.window, Point(x, y), 'float', 'Latitude North: ', length, default_val=north
        )
        self.inputs.append(self.input_n)
        west = self.config_data["map_data"]["coords_west"]
        y += margin_top
        self.input_w = InputBox(
            self.window, Point(x, y), 'float', 'Longitude West: ', length, default_val=west
        )
        self.inputs.append(self.input_w)
        south = self.config_data["map_data"]["coords_south"]
        y += margin_top
        self.input_s = InputBox(
            self.window, Point(x, y), 'float', 'Latitude South: ', length, default_val=south
        )
        self.inputs.append(self.input_s)
        east = self.config_data["map_data"]["coords_east"]
        y += margin_top
        self.input_e = InputBox(
            self.window, Point(x, y), 'float', 'Longitude East: ', length, default_val=east
        )
        self.inputs.append(self.input_e)

        y += margin_top
        divider_text = "-" * 60
        divider = HeaderText(self.window, Point(x, y), divider_text, font_size=font_size, align="center")
        self.labels.append(divider)

        y += margin_top
        self.input_zip_code = InputBox(
            self.window, Point(x, y), 'unsigned_int', 'Zip Code: ', length,
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

        # Simulation Parameters Section
        x = 800
        y = 100
        sim_param_header = HeaderText(self.window, Point(x, y), 'Simulation Parameters', align="center")
        self.labels.append(sim_param_header)

        num_cars = self.config_data["num_cars"]
        y += margin_top + 10
        self.input_num_cars = InputBox(
            self.window, Point(x, y), 'unsigned_int', 'Number of Cars', length, default_val=num_cars
        )
        self.inputs.append(self.input_num_cars)

    def draw_menu(self):
        self.window.clear()
        self.window.setBackground('white')
        self.window.resetView()
        self.load_config_data()

        for hidden_window in self.hidden_windows:
            hidden_window.forget()

        elements = self.buttons + self.inputs + self.labels
        for element in elements:
            element.draw()

    @lru_cache(maxsize=1)
    def get_zip_code_data(self):
        filename = "us_zip_codes.csv"
        return csv_to_dict(filename)

    def fetch_and_save_map_data(self):
        map_filename = self.map_filename
        if os.path.exists(map_filename):
            return
        N = self.input_n.input_text
        W = self.input_w.input_text
        S = self.input_s.input_text
        E = self.input_e.input_text
        overpass_query = query_roads_by_lat_lon(S, W, N, E)
        save_raw_json_map_data(overpass_query, map_filename)

    @property
    def map_filename(self):
        N = self.input_n.input_text
        W = self.input_w.input_text
        S = self.input_s.input_text
        E = self.input_e.input_text
        filename = "_".join([N, W, S, E]) + ".txt"
        map_filename = os.path.join(MAP_DATA_DIR, filename)
        return map_filename

    def simulation_btn_click(self):
        self.fetch_and_save_map_data()
        self.set_config_data()
        self.callback()

    def populate_coords_from_zip(self):
        zip_code = self.input_zip_code.input_text
        zip_code_data = self.get_zip_code_data()

        if zip_code not in zip_code_data:
            return

        lat_spread = 0.00750
        long_spread = 0.0150
        longitude = float(zip_code_data[zip_code]["INTPTLONG"])
        latitude = float(zip_code_data[zip_code]["INTPTLAT"])
        north = latitude + lat_spread
        south = latitude - lat_spread
        west = longitude - long_spread
        east = longitude + long_spread
        self.input_n.set_input(north)
        self.input_s.set_input(south)
        self.input_w.set_input(west)
        self.input_e.set_input(east)

    def run(self):
        self.draw_menu()

        while True:
            last_clicked_pt = self.window.getMouse()
            if last_clicked_pt is not None and self.valid_inputs:
                for button in self.buttons:
                    button.clicked(last_clicked_pt)

    def load_config_data(self):
        self.input_num_cars.set_input(self.config_data["num_cars"])
        self.input_s.set_input(self.config_data["map_data"]["coords_south"])
        self.input_w.set_input(self.config_data["map_data"]["coords_west"])
        self.input_n.set_input(self.config_data["map_data"]["coords_north"])
        self.input_e.set_input(self.config_data["map_data"]["coords_east"])

    def set_config_data(self):
        filename = "config.yml"
        self.config_data = {
            "num_cars": int(self.input_num_cars.input_text),
            "map_data": {
                "filename": self.map_filename,
                "coords_south": self.input_s.input_text,
                "coords_west": self.input_w.input_text,
                "coords_north": self.input_n.input_text,
                "coords_east": self.input_e.input_text,
            }
        }
        save_yaml(filename, self.config_data)

    def valid_inputs(self):
        result = True
        for input_box in self.inputs:
            result |= input_box.validate_input()
        return result
