import random
from graphs import ShortestPaths, Edge


class GPS:
    def __init__(self, graph):
        self.graph = graph
        # self.road_map = ? -> can I avoid this dependency
        # separate class that handles lane_adjustments?
        # how to handle different adjustments for different types of roads?

    def getCoordinates(self, vertex_id):
        vertex = self.graph.vertices[vertex_id]
        # TODO return lane_adjusted point based on car's lane_index
        return (vertex.x, vertex.y)

    def getRoad(self, source_vertex_id, dest_vertex_id):
        possible_edges = self.graph.vertices[source_vertex_id].getEdges()
        for edge in possible_edges:
            if edge.dest == dest_vertex_id:
                return edge
        return None

    def randomVertex(self):
        vertices = list(self.graph.vertices.keys())
        vertex_id = random.choice(vertices)
        return vertex_id

    def shortestRoute(self, source_id, dest_id):
        route = []
        source = self.graph.vertices[source_id]
        shortest_paths = ShortestPaths(self.graph, source)
        dest = dest_id
        route.append(dest)
        while (dest != source.id):
            edge = shortest_paths.path_of_edges.get(dest)
            if edge is None:
                return None  # no route exists
            dest = edge.source
            route.append(dest)
        return route

# TODO
# add method to detect if route exists or ensure all vertices can be reached during creation
