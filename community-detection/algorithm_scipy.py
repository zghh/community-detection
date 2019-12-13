import numpy as np
from sklearn import linear_model
from sklearn.cluster import k_means
import scipy as sp
import math
import queue
from tqdm import tqdm


def find_geodesic_distances(graph, a):
    n = a.shape[0]
    nodes = graph.nodes()
    index = {nodes[i]: i for i in range(n)}
    p = sp.sparse.lil_matrix((n, n))
    for i in range(n):
        temp = np.zeros(n)
        q = queue.Queue()
        q.put((nodes[i], 0))
        while not q.empty():
            (v, c) = q.get()
            for t in list(graph.adj[v]):
                if temp[index[t]] == 0:
                    temp[index[t]] = c + 1
                    q.put((t, c + 1))
        p[i] = temp
    return p


def find_score(p, sigma=10):
    n = p.shape[0]
    s = sp.sparse.lil_matrix((n, n))
    (x, y) = p.nonzero()
    for i in range(len(x)):
        t = p[x[i], y[i]]
        s[x[i], y[i]] = math.exp(-t * t / (2 * sigma ** 2))
    for i in range(n):
        s[i, i] = 1.0
    return s


def _find_symmetric_linear_coefficients(index, n, v, u):
    alpha = 1.0
    for i in range(15):
        lasso = linear_model.Lasso(alpha=alpha, fit_intercept=False)
        lasso.fit(v, u)
        if sum(lasso.coef_) != 0:
            return lasso.coef_ / sum(lasso.coef_)
        alpha /= 2
    return np.array([1 if i == index else 0 for i in range(n)])


def find_symmetric_linear_coefficients(s):
    n = s.shape[0]
    f = sp.sparse.lil_matrix((n, n))
    for i in tqdm(range(n)):
        u = s[:, i]
        v = s
        v[:, i] = 0
        a = _find_symmetric_linear_coefficients(i, n, v, u.toarray()[:, 0])
        a = a / max(a)
        s[:, i] = u
        f[i, :] = f[i, :] + a
    f = (f + np.transpose(f)) / 2
    return f


def find_degree_matrix(f):
    n = f.shape[0]
    _d = [np.sum(row) for row in f]
    d = sp.sparse.lil_matrix((n, n))
    for i in range(n):
        d[i, i] = _d[i]
    return d


def find_laplacian_matrix(d, f):
    n = d.shape[0]
    _d = sp.sparse.lil_matrix((n, n))
    for i in range(n):
        _d[i, i] = math.sqrt(1.0 / d[i, i])
    l = sp.sparse.eye(n) - _d @ f @ _d
    return l


def find_eigen_vectors(l, k=10):
    values, vectors = sp.sparse.linalg.eigs(l, k=k, which="SM")
    return vectors


def find_low_error_clusters(e, n_clusters):
    centroid, labels, inertia, best_n_iter = k_means(e.real, n_clusters=n_clusters, return_n_iter=True)
    print(inertia ** 0.5 / n_clusters)
    return labels, inertia ** 0.5 / n_clusters
