import random
from graphs import ShortestPaths


class GPS:
    def __init__(self, graph):
        self.graph = graph

    def getCoordinates(self, vertex_id):
        vertex = self.graph.vertices[vertex_id]
        return (vertex.x, vertex.y)

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
            edge = shortest_paths.path_of_edges[dest]
            dest = edge.source
            route.append(dest)
        return route

# TODO 
# add method to detect if route exists or ensure all vertices can be reached during creation
