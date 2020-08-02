import numpy as np
from scipy.spatial.distance import cdist


def kmeans_init_centers(X, num_centers):
    # randomly pick k rows of X as initial centers
    centers_pos = np.random.choice(X.shape[0], num_centers, replace=False)
    centers = X[centers_pos]
    return (centers, centers_pos)


def kmeans_assign_labels(X, centers):
    # calculate pairwise distances btw data and centers
    D = cdist(X, centers)
    # return index of the closest center
    return np.argmin(D, axis=1)


def kmeans_update_centers(X, labels, num_centers):
    centers = np.zeros((num_centers, X.shape[1]))
    for k in range(num_centers):
        # collect all points assigned to the k-th cluster
        # lấy những X có label = k
        Xk = X[labels == k, :]
        # print("Xk=", Xk)
        print("labels=", labels)
        # take average
        centers[k, :] = np.mean(Xk, axis=0)
        print("centers=", np.mean(Xk, axis=0), centers[k, :])
    return centers


def has_converged(centers, new_centers):
    # return True if two sets of centers are the same
    return (set([tuple(a) for a in centers]) ==
            set([tuple(a) for a in new_centers]))


def kmeans(X, num_centers):
    (center_list, centers_pos) = kmeans_init_centers(X, num_centers)
    centers = [center_list]
    labels = []
    it = 0
    while True:
        labels.append(kmeans_assign_labels(X, centers[-1]))
        new_centers = kmeans_update_centers(X, labels[-1], num_centers)
        if has_converged(centers[-1], new_centers):
            break
        centers.append(new_centers)
        it += 1
    return (centers, labels, it)


def run():
    means = [[2, 2], [8, 3], [3, 6]]

    cov = [[1, 0], [0, 1]]
    N = 500
    # Lấy 500 điểm từ mỗi cụm trong 3 cụm
    X0 = np.random.multivariate_normal(means[0], cov, N)
    X1 = np.random.multivariate_normal(means[1], cov, N)
    X2 = np.random.multivariate_normal(means[2], cov, N)

    X = np.concatenate((X0, X1, X2), axis=0)
    num_centers = 3
    (centers, labels, it) = kmeans(X, num_centers)
    # indices = [ in centers,:]
    print("X=", X)
