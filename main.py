import pdb
import time
import sys

from graphics import GraphWin, GraphicsError
from ui import Text, Point
from menu import MainMenu
from graphs import Graph, ShortestPaths
from maps import RoadMap
from cars import Car
from info_window import InfoWindow


def main():
    window.setBackground('white')
    window.clear()
    secondary_window.setBackground('white')
    secondary_window.clear()

    info = InfoWindow(secondary_window)

    graph = Graph()
    graph.loadMap("map_default.yml")
    road_map = RoadMap(graph, window)
    road_map.draw()

    source_vertex = graph.vertices["5th Ave|12th St"]
    car = Car(graph, source_vertex)
    car.draw(window)
    # shortest_paths = ShortestPaths(graph, vertex1)

    # initialize simulation variables
    simTime = 0.0
    limit = 10000
    TICKS_PER_SECOND = 60
    TIME_PER_TICK = 1.0/TICKS_PER_SECOND
    nextLogicTick = TIME_PER_TICK
    lastFrameTime = time.time()
    lag = 0.0

    # Main Simulation Loop
    while simTime < limit:
        currentTime = time.time()
        elapsed = currentTime - lastFrameTime
        lastFrameTime = currentTime
        lag += elapsed
        simTime += elapsed

        # process events
        try:
            if window.checkKey() == "space":
                pause()
                lastFrameTime = time.time()
        except GraphicsError:
            pass

        while lag > TIME_PER_TICK:
            # update simulation logic
            car.moveTowardsDest(TIME_PER_TICK)

            nextLogicTick += TIME_PER_TICK
            lag -= TIME_PER_TICK

        # render updates to window
        car.render(window)
        info.updateTable(car.getInfo())

    window.close


def pause():
    """pause until user hits space again"""
    message = Text(Point(window.width/2.0, window.height/2.0 - 50.0), 'Paused')
    message.setSize(24)
    message.draw(window)
    while window.checkKey() != "space":
        pass
    message.undraw()


def cleanup():
    """free resources and close window"""
    window.close()
    sys.exit()


if __name__ == '__main__':
    window = GraphWin('Traffic Simulation', 1024, 768, autoflush=False)
    main_menu = MainMenu(window, main)
    menu_options = {"Menu": main_menu.run, "Restart": main, "Exit": cleanup}
    window.addMenu(menu_options)

    secondary_window = GraphWin('Info Window', 512, 256, autoflush=False)

    main()

# TODO
# set up graph where each intersection represents a vertex
# create road class that defines lanes, intersections, name, speed limit, and collision information
# create car class that defines id (license plate #?), size, preferred speed, start and dest
# AI so cars can change lanes without crashing and adjust route based on existing traffic conditions
# Algo to find shortest path/quickest expected path
# use optparser to initially take command line args
# create gui menu so that settings can be changed in the simulation (# of cars, lane closures, etc)
# create a run simulation method
# feature to import existing road systems from Google Maps API?
