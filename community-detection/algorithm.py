import numpy as np
from sklearn import linear_model
from sklearn.cluster import k_means
from sklearn.metrics import normalized_mutual_info_score
import math
from tqdm import tqdm
import multiprocessing
import numba
import matplotlib.pyplot as plt


@numba.jit(nopython=True)
def find_geodesic_distances(graph, a):
    n = a.shape[0]
    _max = n + 10
    p = [[_max for j in range(n)] for i in range(n)]
    for i in range(n):
        p[i][i] = 0
        q = [(i, 0)]
        start, end = 0, 1
        while start < end:
            (v, c) = q[start]
            for t in graph[v]:
                if p[i][t] == _max:
                    p[i][t] = c + 1
                    q.append((t, c + 1))
                    end += 1
            start += 1
    return np.array(p)


@numba.jit(nopython=True)
def find_score(p, sigma=10):
    n = p.shape[0]
    _max = n + 10
    s = [[0 if p[i, j] == _max else math.exp(-p[i, j] * p[i, j] / (2 * sigma ** 2)) for j in range(n)] for i in
         range(n)]
    return np.array(s)


def _find_symmetric_linear_coefficients_with_lasso(index, n, v, u):
    alpha = 1.0
    for i in range(10):
        lasso = linear_model.Lasso(alpha=alpha, fit_intercept=False, precompute=True)
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


def find_symmetric_linear_coefficients(s, job=0):
    n = s.shape[0]
    f = np.zeros([n, n])
    if job > 0:
        multiprocessing.freeze_support()
        number_process = job
        pool = multiprocessing.Pool(processes=number_process - 1)
        per = int(n / number_process)
        result = []
        for i in range(number_process - 1):
            index = [j for j in range(per * i, per * (i + 1))]
            result.append(pool.apply_async(_find_symmetric_linear_coefficients, args=(s, n, index,)))
        pool.close()
        index = [j for j in range(per * (number_process - 1), n)]
        f[per * (number_process - 1):n, :] = f[per * (number_process - 1):n, :] + _find_symmetric_linear_coefficients(s,
                                                                                                                      n,
                                                                                                                      index)
        pool.join()

        for i in range(number_process - 1):
            p, q = per * i, per * (i + 1)
            f[p:q, :] = f[p:q, :] + result[i].get()
    else:
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


def _find_eigen_vectors(values, vectors, index, k=10):
    return np.array([vectors.transpose()[index[i]] for i in range(k)]).transpose()


def _find_vectors(l):
    values, vectors = np.linalg.eig(l)
    index = values.argsort()
    return values, vectors, index


def find_low_error_clusters(real_labels, ls, la, k=7, max_iter=1000, tol=1e-2, file_name=None):
    x, y = [], []
    k = min(k, ls.shape[0])
    max_iter = min(max_iter, ls.shape[0])
    es_values, es_vector, es_index = _find_vectors(ls)
    ea_values, ea_vector, ea_index = _find_vectors(la)
    result, nmi = [], []
    for n_clusters in range(2, max_iter + 1):
        es = _find_eigen_vectors(es_values, es_vector, es_index, k=k)
        ea = _find_eigen_vectors(ea_values, ea_vector, ea_index, k=k)
        e = np.column_stack((ea[:, :], es[:, :]))
        print(e.shape)
        labels, accumulative_error = _find_clusters(e, n_clusters)
        result.append(labels)
        nmi.append(normalized_mutual_info_score(real_labels, labels))
        x.append(n_clusters)
        y.append(accumulative_error)
        if n_clusters >= 4 and abs(
                (y[n_clusters - 4] - y[n_clusters - 3]) - (y[n_clusters - 3] - y[n_clusters - 2])) / y[0] < tol:
            break
    y = _normalization(y)
    plt.plot(x, y, label='Accumulative Error')
    plt.scatter(x, y)
    plt.plot(x, nmi, label='NMI')
    plt.xticks(x)
    plt.grid()
    plt.title(file_name)
    plt.legend()
    plt.savefig('../result/' + file_name + '.png')
    plt.show()
    return result[len(result) - 3]


def _find_clusters(e, n_clusters):
    centroid, labels, inertia, best_n_iter = k_means(e.real, n_clusters=n_clusters, return_n_iter=True)
    print(inertia ** 0.5 / n_clusters)
    return labels, inertia ** 0.5 / n_clusters


def _normalization(x):
    _min = min(x)
    _max = max(x)
    for i in range(len(x)):
        x[i] = (x[i] - _min) / (_max - _min)
    return x
