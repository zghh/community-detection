import networkx
from numba import types
from numba.typed import Dict
import numpy as np


def load_data():
    graph = networkx.Graph()
    for i in range(6):
        graph.add_node(i)
    for i in range(3):
        for j in range(3):
            if i != j:
                graph.add_edge(i, j)
    for i in range(3, 6):
        for j in range(3, 6):
            if i != j:
                graph.add_edge(i, j)
    graph.add_edge(2, 3)
    graph.add_edge(3, 2)
    return _get_graph(graph), networkx.to_numpy_matrix(graph).A, [0, 0, 0, 1, 1, 1]


def load_data_from_gml(file_name):
    if file_name == 'karate':
        graph = networkx.karate_club_graph()
    else:
        graph = networkx.read_gml('../data/' + file_name + '.gml')

    labels = []
    for i in graph:
        if file_name == 'karate':
            labels.append(graph.nodes[i]['club'])
        else:
            labels.append(graph.nodes[i]['value'])

    print(graph.number_of_nodes(), graph.number_of_edges())
    matrix = networkx.to_numpy_matrix(graph).A
    return _get_graph(graph), matrix, labels


def _get_graph(graph):
    n = graph.number_of_nodes()
    nodes = list(graph.nodes())
    index = {nodes[i]: i for i in range(n)}
    r = {}
    for node in nodes:
        for t in list(graph.adj[node]):
            if index[node] in r:
                r[index[node]].append(index[t])
            else:
                r[index[node]] = [index[t]]
    result = Dict.empty(key_type=types.intp, value_type=types.int32[:], )
    for i in range(n):
        result[i] = np.asarray(r[i])
    return result


def load_lrf_data(file_name, n=1000, average_degree=20, max_degree=50, min_community=30, max_community=100):
    mu = float(file_name[4:])
    graph = networkx.generators.community.LFR_benchmark_graph(n, 2.5, 2.5, mu, average_degree=average_degree,
                                                              max_degree=max_degree,
                                                              min_community=min_community, max_community=max_community)
    communities = {frozenset(graph.nodes[v]['community']) for v in graph}
    print(len(communities))
    labels = []
    for i in range(n):
        t = 0
        for s in communities:
            t = t + 1
            if i in s:
                labels.append(t)
                break
    print(graph.number_of_nodes(), graph.number_of_edges())
    matrix = networkx.to_numpy_matrix(graph).A
    return _get_graph(graph), matrix, labels
