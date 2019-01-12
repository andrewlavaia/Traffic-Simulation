import file_utils
import math
import heapq

class Graph:
    def __init__(self):
        self.vertices = {} # vertex_id: Vertex
        self.vertex_cnt = 0
        self.edge_cnt = 0

    def __repr__(self):
        ret = "Number of vertices: " + str(self.vertex_cnt) + "\n"
        ret += "Number of edges: " + str(self.edge_cnt) + "\n"
        for vertex_id, vertex in self.vertices.items():
            ret += str(vertex_id) + ": " + str(vertex.getEdges()) + "\n"
        return ret

    def loadMap(self, filename):
        data = file_utils.load_map(filename)
        for intersection_id in data["intersections"]:
            self.vertices[intersection_id] = Vertex(intersection_id)
            self.vertex_cnt += 1

        for connection in data["connections"]:
            edge = Edge(connection[0], connection[1], 1)
            self.addEdge(edge)

    def addEdge(self, edge):
        self.vertices[edge.source].addEdge(edge)
        self.edge_cnt +=1

    def adjEdges(self, v):
        return self.vertices[v.id].getEdges()


class Edge:
    def __init__(self, vertex_1, vertex_2, weight):
        self.source = vertex_1
        self.dest = vertex_2
        self.weight = weight

    def __repr__(self):
        return str(self.source) + "->" + str(self.dest) + " (" + str(self.weight) + ")"


class Vertex:
    def __init__(self, name):
        self.id = name
        self.edges = [] # list of connected Edges
        # x y coordinates so it can be drawn?

    def __eq__(self, that):
        return self.id == that.id

    def __lt__(self, that):
        """used to break ties"""
        return self.id < that.id

    def __repr__(self):
        return str(self.id) + ":" + str(self.edges)

    def addEdge(self, edge):
        self.edges.append(edge)

    def getEdges(self):
        return self.edges


class ShortestPaths:
    """Uses Dijkstra's algorithm to build a shortest path tree to each vertex"""
    def __init__(self, graph, source_vertex):
        self.path_of_edges = {}  # dest vertex id: connected edge along shortest path
        self.path_lengths = {}   # dest vertex id: sum of all edge weights along path
        self.pq = []             # list of tuples -> (distance to vertex, vertex)

        for vertex_id in graph.vertices.keys():
            self.path_lengths[vertex_id] = math.inf
        self.path_lengths[source_vertex.id] = 0

        heapq.heappush(self.pq, (0.0, source_vertex))
        while len(self.pq) != 0:
            distance, vertex = heapq.heappop(self.pq)
            self.relax_edges(graph, vertex)

    def relax_edges(self, graph, source_vertex):
        for edge in graph.adjEdges(source_vertex):
            dest_vertex = graph.vertices[edge.dest]

            if self.path_lengths[dest_vertex.id] > self.path_lengths[source_vertex.id] + edge.weight:
                old_length = self.path_lengths[dest_vertex.id]
                self.path_lengths[dest_vertex.id] = self.path_lengths[source_vertex.id] + edge.weight
                self.path_of_edges[dest_vertex.id] = edge

                if (old_length, dest_vertex) in self.pq:
                    index = self.pq.index((old_length, dest_vertex))
                    self.pq[index] = (self.path_lengths[dest_vertex.id], dest_vertex)
                    heapq.heapify(self.pq)

                else:
                    heapq.heappush(self.pq, (self.path_lengths[dest_vertex.id], dest_vertex))


class MapCreator:
    """create a random map from a given number of vertices and edges"""
    pass 
