import random
from graphs import ShortestPaths


class GPS:
    def __init__(self, graph):
        self.graph = graph

    def getVertex(self, vertex_id):
        return self.graph.vertices[vertex_id]

    def randomVertex(self):
        vertices = list(self.graph.vertices.keys())
        vertex_id = random.choice(vertices)
        return self.graph.vertices[vertex_id]

    def shortestRoute(self, source, dest):
        route = []
        shortest_paths = ShortestPaths(self.graph, source)
        dest = dest.id
        route.append(dest)
        while (dest != source.id):
            edge = shortest_paths.path_of_edges[dest]
            dest = edge.source
            route.append(dest)
        return route
