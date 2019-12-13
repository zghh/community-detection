import numpy as np
from sklearn import linear_model
from sklearn.cluster import k_means
import math
import queue
from tqdm import tqdm
import multiprocessing


def find_geodesic_distances(graph, a):
    n = a.shape[0]
    _max = n + 10
    # p = [[1 if a[i, j] == 1 else (0 if i == j else _max) for j in range(n)] for i in range(n)]
    # for k in range(n):
    #     for i in range(n):
    #         for j in range(n):
    #             p[i][j] = min(p[i][j], p[i][k] + p[k][j])
    nodes = graph.nodes()
    index = {nodes[i]: i for i in range(n)}
    p = [[_max for j in range(n)] for i in range(n)]
    for i in range(n):
        p[i][i] = 0
        q = queue.Queue()
        q.put((nodes[i], 0))
        while not q.empty():
            (v, c) = q.get()
            for t in list(graph.adj[v]):
                if p[i][index[t]] == _max:
                    p[i][index[t]] = c + 1
                    q.put((t, c + 1))
    return np.array(p)


def find_score(p, sigma=10):
    n = p.shape[0]
    _max = n + 10
    s = [[0 if p[i, j] == _max else math.exp(-p[i, j] * p[i, j] / (2 * sigma ** 2)) for j in range(n)] for i in
         range(n)]
    return np.array(s)


def _find_symmetric_linear_coefficients_with_lasso(index, n, v, u):
    alpha = 1.0
    for i in range(10):
        lasso = linear_model.Lasso(alpha=alpha, fit_intercept=False)
        lasso.fit(v, u)
        if sum(lasso.coef_) != 0:
            return lasso.coef_ / sum(lasso.coef_)
        alpha /= 2
    return np.array([1 if i == index else 0 for i in range(n)])


def _find_symmetric_linear_coefficients(s, n, index):
    f = np.zeros([len(index), n])
    for i in index:
        u = s[:, i]
        v = np.column_stack((s[:, :i], np.zeros([n, 1]), s[:, i + 1:]))
        a = _find_symmetric_linear_coefficients_with_lasso(i, n, v, u)
        a = a / max(a)
        f[i - index[0], :] = f[i - index[0], :] + a
    return f


def find_symmetric_linear_coefficients(s):
    n = s.shape[0]
    f = np.zeros([n, n])
    # multiprocessing.freeze_support()
    # number_process = 8
    # pool = multiprocessing.Pool(processes=number_process - 1)
    # per = int(n / number_process)
    # result = []
    # for i in range(number_process - 1):
    #     index = [j for j in range(per * i, per * (i + 1))]
    #     result.append(pool.apply_async(_find_symmetric_linear_coefficients, args=(s, n, index,)))
    # pool.close()
    # index = [j for j in range(per * (number_process - 1), n)]
    # f[per * (number_process - 1):n, :] = f[per * (number_process - 1):n, :] + _find_symmetric_linear_coefficients(s, n,
    #                                                                                                               index)
    # pool.join()
    #
    # for i in range(number_process - 1):
    #     p, q = per * i, per * (i + 1)
    #     f[p:q, :] = f[p:q, :] + result[i].get()
    for i in tqdm(range(n)):
        u = s[:, i]
        v = np.column_stack((s[:, :i], np.zeros([n, 1]), s[:, i + 1:]))
        a = _find_symmetric_linear_coefficients_with_lasso(i, n, v, u)
        a = a / max(a)
        f[i, :] = f[i, :] + a
    f = (f + np.transpose(f)) / 2
    return f


def find_degree_matrix(f):
    _d = [np.sum(row) for row in f]
    d = np.diag(_d)
    return d


def find_laplacian_matrix(d, f):
    n = d.shape[0]
    _d = np.power(np.linalg.matrix_power(d, -1), 0.5)
    l = np.identity(n) - (_d.dot(f)).dot(_d)
    return l


def find_eigen_vectors(l, k=10):
    values, vectors = np.linalg.eig(l)
    _v = list(enumerate(values))
    _v.sort(key=lambda element: element[1])
    return np.array([vectors.transpose()[_v[i][0]] for i in range(k)]).transpose()


def find_low_error_clusters(e, n_clusters):
    centroid, labels, inertia, best_n_iter = k_means(e.real, n_clusters=n_clusters, return_n_iter=True)
    print(inertia ** 0.5 / n_clusters)
    return labels, inertia ** 0.5 / n_clusters
