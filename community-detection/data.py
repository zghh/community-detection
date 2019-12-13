import networkx


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
    return graph, networkx.to_numpy_matrix(graph).A


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

    print(graph.number_of_nodes(), graph.number_of_edges())
    matrix = networkx.to_numpy_matrix(graph).A
    return graph, matrix
