import time
import sys

from graphics import GraphApp, GraphWin, Text, Point, _root
from menu import MainMenu
from graphs import Graph, ShortestPaths
from maps import RoadMap
from cars import Car, CarShape, CarFactory
from gps import GPS
from info_window import InfoWindow
from collision import GridCollisionSystem, QuadTreeCollisionSystem
from latlon import LatLonConverter
from openstreetmap import query_roads_by_lat_lon, save_raw_json_map_data


def main():
    window.addToParent()
    window.setBackground('white')
    window.clear()
    window.resetView()
    secondary_window.addToParent()
    secondary_window.setBackground('white')
    secondary_window.clear()

    config_data = main_menu.config_data or {}

    S = config_data["coords_south"]
    W = config_data["coords_west"]
    N = config_data["coords_north"]
    E = config_data["coords_east"]
    # S, W, N, E = "40.73489", "-73.99264", "40.74020", "-73.97923"  # NYC lower east side
    # S, W, N, E = "40.9946", "-73.8817", "41.0174", "-73.8281"  # lower westchester
    # overpass_query = query_roads_by_lat_lon(S, W, N, E)
    # save_raw_json_map_data(overpass_query, "map_data.txt")

    llc = LatLonConverter(window, S, W, N, E)

    graph = Graph()
    graph.load_open_street_map_data("map_data.txt", llc)
    # graph.load_open_street_map_data("map_data2.txt", llc)

    road_map = RoadMap(graph, window)
    road_map.draw()
    road_map.draw_road_names()

    gps = GPS(graph, road_map)

    cars = []
    car_shapes = []
    car_factory = CarFactory(window, gps, cars, car_shapes)

    num_cars = config_data["num_cars"]
    for i in range(num_cars):
        car_factory.create()

    # collision_system = GridCollisionSystem(window, cars)
    collision_system = QuadTreeCollisionSystem(window, cars)

    info = InfoWindow(secondary_window)
    info.set_selected_car(cars[0])
    info.initialize_table()
    car_shapes[info.selected_car.index].shape.setFill("yellow")

    for car_shape in car_shapes:
        car_shape.draw()

    # initialize simulation variables
    simTime = 0.0
    limit = 10000
    TICKS_PER_SECOND = 30
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
        window.update()
        secondary_window.update()
        frame.update()
        last_pressed_key = window.checkKey() or secondary_window.checkKey()
        if last_pressed_key is not None:
            if last_pressed_key == "space":
                pause()
                lastFrameTime = time.time()
            elif last_pressed_key == "p":
                window.zoomIn()
            elif last_pressed_key == "o":
                window.zoomOut()
            elif last_pressed_key == "d":
                print(road_map.getRoadsWithinView())

        last_clicked_pt = window.checkMouse()
        if last_clicked_pt is not None:
            for car_shape in car_shapes:
                if car_shape.clicked(last_clicked_pt):
                    car_shapes[info.selected_car.index].shape.setFill("white")
                    info.set_selected_car(cars[car_shape.index])
                    car_shapes[info.selected_car.index].shape.setFill("yellow")
                    continue

            for intersection in road_map.intersections.values():
                if intersection.clicked(last_clicked_pt):
                    road_map.show_info(intersection)
                    continue

        last_clicked_pt = secondary_window.checkMouse()
        if last_clicked_pt is not None:
            secondary_window.update()
            for button in info.buttons:
                button.clicked(last_clicked_pt)
                continue

        # update simulation logic
        while lag > TIME_PER_TICK:
            collision_system.process_collisions(cars)
            for car in cars:
                car.move_towards_dest(TIME_PER_TICK)
                car_shape = car_shapes[car.index]
                car_shape.x = cars[car.index].x
                car_shape.y = cars[car.index].y
            collision_system.update_objects(cars)

            nextLogicTick += TIME_PER_TICK
            lag -= TIME_PER_TICK

        # render updates to window
        for car_shape in car_shapes:
            car_shape.render()

        info.updateTable()
        if info.follow_car:
            window.centerScreenOnPoint(info.selected_car.x, info.selected_car.y)

        road_map.draw_route(info.selected_car, info.show_route)

        _root.update_idletasks()

    window.close()
    secondary_window.close()
    frame.close()


def pause():
    """pause until user hits space again"""
    cx, cy = window.getCenterScreenPoint()
    message = Text(Point(cx, cy), 'Paused')
    message.setSize(24)
    message.draw(window)
    while window.checkKey() != "space" and secondary_window.checkKey() != "space":
        window.update()
        secondary_window.update()
    message.undraw()


def cleanup():
    """free resources and close window"""
    window.close()
    secondary_window.close()
    frame.close()
    sys.exit()


if __name__ == '__main__':
    frame = GraphApp("Traffic Simulation")
    window_options = {"pack": {"side": "left", "fill": "both", "expand": True}}
    window = GraphWin(
        "Map Window", 1280, 800, autoflush=False,
        new_window=False, master=frame.master, master_options=window_options
    )
    secondary_window_options = {"place": {"relx": 1, "rely": 0, "anchor": "ne"}}
    secondary_window = GraphWin(
        "Info Window", 300, 400, autoflush=False, scrollable=False,
        new_window=False, master=frame.master, master_options=secondary_window_options
    )
    main_menu = MainMenu(window, main, secondary_window=secondary_window)
    menu_options = {"Menu": main_menu.run, "Restart": main, "Exit": cleanup}
    frame.addMenu(menu_options)

    main()

# TODO
# AI so cars can change lanes without crashing and adjust route based on existing traffic conditions
    # add ability for cars to change lanes
# create gui menu so that settings can be changed in the simulation (# of cars, lane closures, etc)
# increase # of cars that can be drawn on the screen at once to: 500 | 1000
# dynamically load additional map data when zooming out or moving camera
