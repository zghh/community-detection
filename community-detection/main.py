from data import load_data, load_data_from_gml, load_lrf_data
from algorithm import find_geodesic_distances, find_score, find_symmetric_linear_coefficients, find_degree_matrix, \
    find_laplacian_matrix, find_low_error_clusters
import time
from database import add_graph


def test_lrf():
    t = 10
    mu = 0.3
    while mu <= 0.7:
        print('----------mu={:.2f}----------'.format(mu))
        average_nmi, average_time = 0, 0
        for p in range(t):
            print('----------i={:d}----------'.format(p))
            start = time.time()
            file_name = 'LRF_{:.2f}'.format(mu)
            graph, a, real_labels = load_lrf_data(file_name)
            print("Load time used:", time.time() - start)
            start = time.time()
            p = find_geodesic_distances(graph, a)
            s = find_score(p, sigma=8)
            f = find_symmetric_linear_coefficients(s, alpha=1)
            ds = find_degree_matrix(f)
            da = find_degree_matrix(a)
            ls = find_laplacian_matrix(ds, f)
            la = find_laplacian_matrix(da, a)
            print("Generate time used:", time.time() - start)
            labels, nmi = find_low_error_clusters(real_labels, ls, la, max_iter=100, k=30, tol=1e-4,
                                                  file_name=file_name)
            print(labels)
            print(nmi)
            average_time += time.time() - start
            average_nmi += nmi
            print("Time used:", time.time() - start)
        print('NMI: ', average_nmi / t)
        print('Time: ', average_time / t)

        mu += 0.05


def main():
    # start = time.time()
    # file_name = 'LRF_0.6'
    # graph, a, real_labels = load_lrf_data(file_name)
    # # file_name = 'karate'
    # # graph, a, real_labels = load_data_from_gml(file_name)
    # print("Load time used:", time.time() - start)
    # start = time.time()
    # p = find_geodesic_distances(graph, a)
    # s = find_score(p, sigma=8)
    # f = find_symmetric_linear_coefficients(s, alpha=1)
    # ds = find_degree_matrix(f)
    # da = find_degree_matrix(a)
    # ls = find_laplacian_matrix(ds, f)
    # la = find_laplacian_matrix(da, a)
    # print("Generate time used:", time.time() - start)
    # labels, nmi = find_low_error_clusters(real_labels, ls, la, max_iter=100, k=10, tol=1e-4, file_name=file_name)
    # print(labels)
    # print(nmi)
    # print("Time used:", time.time() - start)
    #
    # # add_graph(a, labels, file_name)

    test_lrf()


if __name__ == '__main__':
    main()
