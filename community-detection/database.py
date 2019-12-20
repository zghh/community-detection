from settings import *
from py2neo import Node, Relationship, Graph
from data import load_data_from_gml


def _connect():
    return Graph(database_url, username=database_username, password=database_password)


def _add_graph(graph, a, name, labels):
    n = a.shape[0]
    nodes = []
    for i in range(n):
        # node = Node(name, name='{:03d}'.format(i))
        # node.add_label(str(labels[i]))
        nodes.append(Node('{:s}_{:d}'.format(name, labels[i]), name='{:03d}'.format(i)))
        graph.create(nodes[i])
    for i in range(n):
        for j in range(i + 1, n):
            if a[i, j] == 1:
                relationship = Relationship(nodes[i], 'normal', nodes[j])
                graph.create(relationship)


def add_graph(a, labels, name):
    graph = _connect()
    _add_graph(graph, a, name, labels)
