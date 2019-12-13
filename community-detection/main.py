from data import load_data, load_data_from_gml
from algorithm import find_geodesic_distances, find_score, find_symmetric_linear_coefficients, find_degree_matrix, \
    find_laplacian_matrix, find_eigen_vectors, find_low_error_clusters
import numpy as np
import matplotlib.pyplot as plt
import time


def main():
    start = time.time()

    graph, a = load_data_from_gml('polblogs')
    # graph, a = load_data()
    print("Load time used:", time.time() - start)
    p = find_geodesic_distances(graph, a)
    s = find_score(p, sigma=5)
    f = find_symmetric_linear_coefficients(s)
    ds = find_degree_matrix(f)
    da = find_degree_matrix(a)
    ls = find_laplacian_matrix(ds, f)
    la = find_laplacian_matrix(da, a)
    print("Generate time used:", time.time() - start)
    x, y = [], []
    for n_clusters in range(2, 15):
        es = find_eigen_vectors(ls, k=7)
        ea = find_eigen_vectors(la, k=7)
        e = np.column_stack((ea[:, :], es[:, :]))
        print(e.shape)
        labels, accumulative_error = find_low_error_clusters(e, n_clusters)
        x.append(n_clusters)
        y.append(accumulative_error)
    plt.plot(x, y)
    plt.scatter(x, y)
    plt.xticks(x)
    plt.grid()
    plt.show()

    print("Time used:", time.time() - start)


if __name__ == '__main__':
    main()
