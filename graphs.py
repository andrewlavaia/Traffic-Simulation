import math
import heapq
import random
import copy
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

    def load_map(self, filename):
        data = file_utils.load_yaml(filename)
        for vertex_data in data["intersections"]:
            intersection_id, x, y = vertex_data
            self.vertices[intersection_id] = Vertex(intersection_id, x, y, None)
            self.vertex_cnt += 1

        for connection in data["connections"]:
            edge = Edge(connection[0], connection[1], 1, None)
            self.add_edge(edge)

    def load_open_street_map_data(self, filename, lat_lon_converter):
        api = overpy.Overpass()
        result = api.parse_json(file_utils.load_bytes(filename))

        for node in result.nodes:
            if self.vertices.get(node.id) is None:
                global_x, global_y = lat_lon_converter.lat_lon_to_global_xy(node.lat, node.lon)
                local_x, local_y = lat_lon_converter.global_xy_to_local_xy(global_x, global_y)
                self.vertices[node.id] = Vertex(node.id, local_x, local_y, node.tags)

        for way in result.ways:
            prev_node = None
            mid_node = None
            for node in way.nodes:
                if prev_node is None:
                    prev_node = node
                    continue

                if mid_node is None:
                    mid_node = node
                    continue

                if self.can_vertices_be_reduced(prev_node.id, mid_node.id, node.id):
                    mid_node = node
                    continue

                self.add_edges(prev_node.id, mid_node.id, way.tags)
                prev_node = mid_node
                mid_node = node

            self.add_edges(prev_node.id, mid_node.id, way.tags)

        self.remove_unused_vertices()

    def add_edge(self, edge):
        self.vertices[edge.source].add_edge(edge)
        self.edge_cnt += 1

    def add_edges(self, v1, v2, tags):
        if v1 and v2 and v1 != v2:
            distance = self.distance_between_vertices(v1, v2)
            edge = Edge(v1, v2, distance, tags)
            self.add_edge(edge)
            if tags.get('oneway') != 'yes':
                other_edge = Edge(v2, v1, distance, tags)
                self.add_edge(other_edge)

    def adj_edges(self, v):
        return self.vertices[v.id].get_edges()

    def distance_between_vertices(self, vertex_id_1, vertex_id_2):
        v1 = self.vertices[vertex_id_1]
        v2 = self.vertices[vertex_id_2]
        dx = v2.x - v1.x
        dy = v2.y - v1.y
        dist = math_utils.pythag(dx, dy)
        return dist

    def can_vertices_be_reduced(self, vertex_id_1, vertex_id_2, vertex_id_3):
        """Check whether 3 vertices can be reduced to 2 vertices"""
        v2 = self.vertices[vertex_id_2]
        if v2.is_intersection:
            return False

        v1 = self.vertices[vertex_id_1]
        dx1 = v2.x - v1.x
        dy1 = v2.y - v1.y
        dist = math_utils.pythag(dx1, dy1)
        if dist < 10.0:
            return True

        v3 = self.vertices[vertex_id_3]
        dx2 = v3.x - v2.x
        dy2 = v3.y - v2.y
        angle1 = math_utils.angle(dx1, dy1)
        angle2 = math_utils.angle(dx2, dy2)
        if abs(angle2 - angle1) < 0.10:  # ~5.7 degrees
            return True

        return False

    def remove_unused_vertices(self):
        """Remove all vertices that aren't a source or dest for an edge"""
        vertices_with_all_edges = copy.deepcopy(self.vertices)
        for vertex_id, vertex in self.vertices.items():
            for edge in vertex.edges:
                vertices_with_all_edges[edge.dest].edges.append(edge.id)

        vertices_to_remove = set()
        for vertex_id, vertex in vertices_with_all_edges.items():
            if not vertex.edges:
                vertices_to_remove.add(vertex_id)

        for vertex_id in vertices_to_remove:
            self.vertices.pop(vertex_id, None)


class Edge:
    def __init__(self, vertex_id_1, vertex_id_2, weight, tags):
        self.id = id(self)
        self.source = vertex_id_1
        self.dest = vertex_id_2
        self.weight = weight
        self.name = tags.get("name", "")
        self.speed_limit = "".join([c for c in str(tags.get("maxspeed", 25)) if c.isdigit()])
        self.lanes = int(tags.get("lanes", 1))
        self.is_one_way = True if tags.get("oneway") == "yes" else False

    def __repr__(self):
        return str(self.source) + "->" + str(self.dest) + " (" + str(self.weight) + ")"

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash((self.id, self.source, self.dest, self.weight, self.name))


class Vertex:
    def __init__(self, vertex_id, x, y, tags):
        self.id = vertex_id
        self.edges = []  # list of connected Edges
        self.x = x
        self.y = y
        self.is_intersection = bool(tags.get("highway") == "traffic_signals")

    def __eq__(self, that):
        return self.id == that.id

    def __repr__(self):
        return str(self.id) + ":" + str(self.edges)

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_edges(self):
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
        for edge in graph.adj_edges(source_vertex):
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
