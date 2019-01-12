import pdb
import time

from graphs import Graph, ShortestPaths


def main():
    graph = Graph()
    graph.loadMap("map_default.yml")
    vertex1 = graph.vertices["5th Ave|12th St"]
    shortest_paths = ShortestPaths(graph, vertex1)
    pdb.set_trace()

if __name__ == '__main__':
    main()

# TODO
# set up graph where each intersection represents a vertex
# create road class that defines lanes, intersections, name, speed limit, and collision information
# create car class that defines id (license plate #?), size, preferred speed, starting point, and ending destination
# AI so cars can change lanes without crashing and adjust route based on existing traffic conditions
# Algo to find shortest path/quickest expected path
# use optparser to initially take command line args
# create gui menu so that settings can be changed in the simulation (# of cars, lane closures, etc)
# create a run simulation method 
# feature to import existing road systems from Google Maps API?
