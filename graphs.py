import math
import heapq
import random
import overpy

import file_utils
import math_utils


class Graph:
    def __init__(self):
        self.vertices = {}  # vertex_id: Vertex
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
        for vertex_data in data["intersections"]:
            intersection_id, x, y = vertex_data
            self.vertices[intersection_id] = Vertex(intersection_id, x, y)
            self.vertex_cnt += 1

        for connection in data["connections"]:
            edge = Edge(connection[0], connection[1], 1, None)
            self.addEdge(edge)

    def loadOpenStreetMapData(self, filename, lat_lon_converter):
        api = overpy.Overpass()
        result = api.parse_json(file_utils.load_bytes(filename))
        nodes = {}

        for node in result.nodes:
            if self.vertices.get(node.id) is None:
                global_x, global_y = lat_lon_converter.latLonToGlobalXY(node.lat, node.lon)
                local_x, local_y = lat_lon_converter.globalXYToLocalXY(global_x, global_y)
                self.vertices[node.id] = Vertex(node.id, local_x, local_y)

        for way in result.ways:
            prev_node = None
            for node in way.nodes:
                if prev_node is not None:
                    # create edge between current node and prev_node
                    edge = Edge(prev_node.id, node.id, 1, way.tags.get('name'))
                    self.addEdge(edge)
                    if not way.tags.get('oneway') or way.tags.get('oneway') != 'yes':
                        other_edge = Edge(node.id, prev_node.id, 1, way.tags.get('name'))
                        self.addEdge(other_edge)
                prev_node = node

    def addEdge(self, edge):
        self.vertices[edge.source].addEdge(edge)
        self.edge_cnt += 1

    def adjEdges(self, v):
        return self.vertices[v.id].getEdges()


class Edge:
    def __init__(self, vertex_id_1, vertex_id_2, weight, name):
        self.source = vertex_id_1
        self.dest = vertex_id_2
        self.weight = weight
        self.name = name

    def __repr__(self):
        return str(self.source) + "->" + str(self.dest) + " (" + str(self.weight) + ")"

    def __eq__(self, other):
        return (
            self.source == other.source and
            self.dest == other.dest and
            self.weight == other.weight
        )


class Vertex:
    def __init__(self, vertex_id, x, y):
        self.id = vertex_id
        self.edges = []  # list of connected Edges
        self.x = x
        self.y = y

    def __eq__(self, that):
        return self.id == that.id

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
        self.pq = []             # list of tuples -> (distance to vertex, vertex_id)

        for vertex_id in graph.vertices.keys():
            self.path_lengths[vertex_id] = math.inf
        self.path_lengths[source_vertex.id] = 0

        heapq.heappush(self.pq, (0.0, source_vertex.id))
        while len(self.pq) != 0:
            distance, vertex_id = heapq.heappop(self.pq)
            vertex = graph.vertices[vertex_id]
            self.relax_edges(graph, vertex)

    def relax_edges(self, graph, source_vertex):
        for edge in graph.adjEdges(source_vertex):
            dest_vertex = graph.vertices[edge.dest]

            dest_length = self.path_lengths[dest_vertex.id]
            source_length = self.path_lengths[source_vertex.id]
            if dest_length > source_length + edge.weight:
                self.path_lengths[dest_vertex.id] = source_length + edge.weight
                self.path_of_edges[dest_vertex.id] = edge

                if (dest_length, dest_vertex.id) in self.pq:
                    index = self.pq.index((dest_length, dest_vertex.id))
                    self.pq[index] = (self.path_lengths[dest_vertex.id], dest_vertex.id)
                    heapq.heapify(self.pq)

                else:
                    heapq.heappush(self.pq, (self.path_lengths[dest_vertex.id], dest_vertex.id))
