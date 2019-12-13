from file_utils import load_yaml
from ui import *


class MainMenu:
    def __init__(self, window, callback, config="config.yml", secondary_window=None):
        self.window = window
        self.secondary_window = secondary_window
        self.callback = callback
        self.buttons = []
        self.config_data = load_yaml(config)

        simulation_btn = Button(
            self.callback, self.window, Point(500, 200), 200, 100, 'Run Simulation'
        )
        test_btn = Button(
            test_func, self.window, Point(500, 400), 200, 100, 'Print Test'
        )
        self.buttons.append(simulation_btn)
        self.buttons.append(test_btn)

    def draw_menu(self):
        self.window.clear()
        self.window.setBackground('white')

        if self.secondary_window:
            self.secondary_window.forget()

        for button in self.buttons:
            button.draw()

    def run(self):
        self.draw_menu()

        while True:
            last_clicked_pt = self.window.getMouse()
            if last_clicked_pt is not None:
                for button in self.buttons:
                    button.clicked(last_clicked_pt)


def test_func():
    print("test")
