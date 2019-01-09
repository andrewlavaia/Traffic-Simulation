import file_utils

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
        return self.vertices[v].getEdges()


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

    def __repr__(self):
        return str(self.id) + ":" + str(self.edges)

    def addEdge(self, edge):
        self.edges.append(edge)

    def getEdges(self):
        return self.edges

class MapCreator:
    """create a random map from a given number of vertices and edges"""
    pass 
