from settings import *
from py2neo import Node, Relationship, Graph
from data import load_data_from_gml


def _connect():
    return Graph(database_url, username=database_username, password=database_password)


def _add_graph(graph, a, name, labels):
    n = a.shape[0]
    for i in range(n):
        node = Node(name, name='{:03d}'.format(i))
        node.add_label(str(labels[i]))
        graph.create(node)
    for i in range(n):
        for j in range(i + 1, n):
            if a[i, j] == 1:
                node_i = graph.nodes.match(name, name='{:03d}'.format(i)).first()
                node_j = graph.nodes.match(name, name='{:03d}'.format(j)).first()
                relationship = Relationship(node_i, 'normal', node_j)
                graph.create(relationship)


def add_graph(a, labels, name):
    graph = _connect()
    _add_graph(graph, a, name, labels)
