from data import load_data, load_data_from_gml
from algorithm import find_geodesic_distances, find_score, find_symmetric_linear_coefficients, find_degree_matrix, \
    find_laplacian_matrix, find_low_error_clusters
import time
from database import add_graph


def main():
    start = time.time()
    file_name = 'polblogs'
    graph, a = load_data_from_gml(file_name)
    # graph, a = load_data()
    print("Load time used:", time.time() - start)
    start = time.time()
    p = find_geodesic_distances(graph, a)
    s = find_score(p, sigma=5)
    f = find_symmetric_linear_coefficients(s)
    ds = find_degree_matrix(f)
    da = find_degree_matrix(a)
    ls = find_laplacian_matrix(ds, f)
    la = find_laplacian_matrix(da, a)
    print("Generate time used:", time.time() - start)
    labels = find_low_error_clusters(ls, la, max_iter=15, k=7)
    print("Time used:", time.time() - start)

    add_graph(a, labels, file_name)


if __name__ == '__main__':
    main()
