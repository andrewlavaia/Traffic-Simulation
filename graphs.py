import file_utils

class Graph:
    def __init__(self):
        self.vertices = {} # vertex_id: Intersection
        self.vertex_cnt = 0
        self.edge_cnt = 0

    def __repr__(self):
        ret = "Number of vertices: " + str(self.vertex_cnt) + "\n"
        ret += "Number of edges: " + str(self.edge_cnt) + "\n"
        for vertex_id, intersection in self.vertices.items():
            ret += vertex_id + ": " + str(intersection.getEdges()) + "\n"
        return ret

    def loadMap(self, filename):
        data = file_utils.load_map(filename)
        for intersection_id in data["intersections"]:
            self.vertices[intersection_id] = Intersection(intersection_id)
            self.vertex_cnt += 1

        for connection in data["connections"]:
            edge = Edge(connection[0], connection[1], 0)
            self.addEdge(edge)

    def addEdge(self, edge):
        v1 = edge.either()
        v2 = edge.other(v1)
        self.vertices[v1].addEdge(edge)
        self.vertices[v2].addEdge(edge)
        self.edge_cnt +=1

    def adjEdges(self, v):
        return self.vertices[v].getEdges()

class Edge:
    def __init__(self, vertex_1, vertex_2, weight):
        self.v1 = vertex_1
        self.v2 = vertex_2
        self.weight = weight
    
    def __repr__(self):
        return ",".join([self.v1, self.v2, str(self.weight)])

    def compare(self, rhs):
        if self.weight < rhs.weight:
            return -1
        elif self.weight > rhs.weight:
            return 1
        else:
            return 0

    def either(self):
        """used when neither edge is known"""
        return self.v1
    
    def other(self, vertex_id):
        """used when one edge is already known"""
        if vertex_id == self.v1:
            return self.v2
        elif vertex_id == self.v2:
            return self.v1
        else:
            raise TypeError(vertex_id + " not found in v1 or v2")


class Intersection:
    def __init__(self, name):
        self.id = name
        self.edges = [] # list of connected Edges
        # x y coordinates so it can be drawn?

    def addEdge(self, edge):
        self.edges.append(edge)

    def getEdges(self):
        return self.edges

class MapCreator:
    """create a random map from a given number of vertices and edges"""
    pass 
    

    