import networkx
import scipy as sp


def load_data():
    a = sp.sparse.lil_matrix((6, 6))
    graph = networkx.Graph()
    for i in range(6):
        graph.add_node(i)
    for i in range(3):
        for j in range(3):
            if i != j:
                graph.add_edge(i, j)
                a[i, j] = 1
    for i in range(3, 6):
        for j in range(3, 6):
            if i != j:
                graph.add_edge(i, j)
                a[i, j] = 1
    graph.add_edge(2, 3)
    a[2, 3] = 1
    graph.add_edge(3, 2)
    a[3, 2] = 1
    return graph, a


def load_data_from_gml(file_name):
    if file_name == 'polblogs':
        with open('../data/' + file_name + '.gml', 'r', encoding='utf-8') as file:
            graph = networkx.parse_gml(file.read().split('\n')[1:])
    else:
        graph = networkx.read_gml('../data/' + file_name + '.gml')

    remove_nodes = []
    for i in graph.nodes():
        if not list(graph.adj[i]):
            remove_nodes.append(i)
    for i in remove_nodes:
        graph.remove_node(i)

    n = graph.number_of_nodes()
    a = sp.sparse.lil_matrix((n, n))
    nodes = graph.nodes()
    index = {nodes[i]: i for i in range(n)}
    for node in nodes:
        for t in list(graph.adj[node]):
            a[index[node], index[t]] = 1
            a[index[t], index[node]] = 1

    print(graph.number_of_nodes(), graph.number_of_edges())
    return graph, a
