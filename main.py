import pdb
import time
import sys

from graphics import GraphWin, GraphicsError
from ui import Text, Point
from menu import MainMenu
from graphs import Graph, ShortestPaths
from maps import RoadMap
from cars import Car
from gps import GPS
from info_window import InfoWindow
from collision import processCollisions
from latlon import LatLonConverter
from openstreetmap import query_roads_by_lat_lon, save_raw_json_map_data


def main():
    window.setBackground('white')
    window.clear()
    secondary_window.setBackground('white')
    secondary_window.clear()

    zoom_factor = 1.0
    window.setCoords(0, window.height/zoom_factor, window.width/zoom_factor, 0)

    info = InfoWindow(secondary_window)

    # S, W, N, E = "40.9946", "-73.8817", "41.0174", "-73.8281"  # lower westchester
    S, W, N, E = "40.73489", "-73.99264", "40.74020", "-73.97923"  # NYC lower east side
    # overpass_query = query_roads_by_lat_lon(S, W, N, E)
    # save_raw_json_map_data(overpass_query, "map_data.txt")

    llc = LatLonConverter(window, S, W, N, E)

    graph = Graph()
    # graph.loadMap("map_default.yml")
    graph.loadOpenStreetMapData("map_data.txt", llc)

    # graph.randomMap(25, 50)
    road_map = RoadMap(graph, window)
    road_map.draw()

    gps = GPS(graph)

    num_cars = 5
    cars = []
    for i in range(0, num_cars):
        car = Car(gps, gps.randomVertex())
        car.draw(window)
        cars.append(car)

    selected_car = cars[0]

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
            last_pressed_key = window.checkKey() or secondary_window.checkKey()
            if last_pressed_key is not None:
                if last_pressed_key == "space":
                    pause()
                    lastFrameTime = time.time()
                elif last_pressed_key == "p":
                    zoom_factor *= 1.1
                    window.setCoords(0, window.height/zoom_factor, window.width/zoom_factor, 0)
                elif last_pressed_key == "o":
                    zoom_factor *= 0.9
                    window.setCoords(0, window.height/zoom_factor, window.width/zoom_factor, 0)

            last_clicked_pt = window.checkMouse()
            if last_clicked_pt is not None:
                for car in cars:
                    if car.clicked(last_clicked_pt):
                        selected_car.shape.setFill("white")
                        selected_car = car

        except GraphicsError:
            pass

        # update simulation logic
        while lag > TIME_PER_TICK:
            processCollisions(cars)
            for car in cars:
                car.moveTowardsDest(TIME_PER_TICK)

            nextLogicTick += TIME_PER_TICK
            lag -= TIME_PER_TICK

        # render updates to window
        for car in cars:
            car.render(window)
        info.updateTable(selected_car.getInfo())
        selected_car.shape.setFill("yellow")

    window.close


def pause():
    """pause until user hits space again"""
    message = Text(Point(window.width/2.0, window.height/2.0 - 50.0), 'Paused')
    message.setSize(24)
    message.draw(window)
    while window.checkKey() != "space" and secondary_window.checkKey() != "space":
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
