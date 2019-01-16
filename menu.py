from ui import *


class MainMenu:
    def __init__(self, window, callback):
        self.window = window
        self.callback = callback
        self.buttons = []

        simulation_btn = Button(
            self.callback, self.window, Point(500, 200), 200, 100, 'Run Simulation'
        )
        test_btn = Button(
            test_func, self.window, Point(500, 400), 200, 100, 'Print Test'
        )
        self.buttons.append(simulation_btn)
        self.buttons.append(test_btn)

    def drawMenu(self):
        self.window.clear()
        self.window.setBackground('white')

        for button in self.buttons:
            button.draw()

    def run(self):
        self.drawMenu()

        while True:
            last_clicked_pt = self.window.getMouse()
            if last_clicked_pt is not None:
                for button in self.buttons:
                    button.clicked(last_clicked_pt)


def test_func():
    print("test")
