
import numpy as np


def get_pair_x_y(graph):
    query = """
        CALL {
            MATCH (bob:Author)-[r:COLLABORATE_TEST]-(lily:Author)
            WHERE bob <> lily
                AND bob.test = TRUE
                AND lily.test = TRUE
                AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
            RETURN DISTINCT bob, lily, 1 AS existed
            UNION
            MATCH (bob:Author)-[r:COLLABORATE_TEST]-(lily:Author)
            WHERE bob <> lily
                AND bob.test = TRUE
                AND lily.test = TRUE
                AND r IS NULL
                AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
            RETURN DISTINCT bob, lily, 0 AS existed
        }
        WITH DISTINCT existed, bob, lily
        WITH DISTINCT existed, COLLECT(bob) AS bob, COLLECT(lily) AS lily
        WITH DISTINCT existed, bob, lily, SIZE(bob) AS size_1,  SIZE(lily) AS size_2
        WITH existed, bob, lily, CASE size_1 > size_2 WHEN TRUE THEN size_2 ELSE size_1 END AS size
        WITH existed, bob, lily, RANGE(0,size - 1,1) AS range
        UNWIND range AS idx
        WITH existed, bob[idx] AS bob, lily[idx] AS lily
        WHERE NOT bob IS NULL OR NOT lily IS NULL
        RETURN existed, bob.author_id AS bob, lily.author_id AS lily
        ORDER BY existed DESC, lily
    """
    toList = graph.run(query)
    toList = list(toList)


def create_training_pair(graph):
    print("create_training_pair: Start")
    """
    Tạo training data từ tập label và data
    """
    query = """
        MATCH (bob:Author)-[r:COLLABORATE_PRIOR ]-(:Author)
        WHERE bob.test=TRUE
        WITH DISTINCT bob.author_id AS author_id, 
            r.score AS x, 
            CASE EXISTS((bob:Author)-[:COLLABORATE_TEST]-(:Author)) WHEN TRUE THEN 1 ELSE -1 END AS y
        RETURN DISTINCT x, y
    """
    toList = graph.run(query)
    toList = list(toList)
    result = [[0.0, -1]
              for idx in range(0, len(toList), 1)]
    for idx, row in enumerate(toList):
        for dimension, value in enumerate(row):
            result[idx][dimension] = row[dimension]

    # print("result=", result)
    print("create_training_pair: End")
    return result


def prepare_training_data(
    training_pairs: list
) -> (list, list, int):
    '''
    input:
    + training_pairs: The format of data shall be [x1, .., xd,y]
    + d: number of dimension of x

    output:
    + X<list>: the matrix of data
        [[ x_11 x_12 x_13 .. x_1N ],
        ..
        [ x_d1 x_d2 x_d3 .. x_dN ],]
    + V<list>:
        [[ x_11*y_1 x_12*y_2 x_13*y_3 .. x_1N*y_N ],
        ..
        [ x_d1*y_1 x_d2*y_2 x_d3*y_3 .. x_dN*y_N ],]
    + y<list>:
        [[ y_11 .. y_1N ],
        ..
        [ y_d1 .. y_dN ],]
    + N<int>: number of training data
    '''
    d = len(training_pairs[0]) - 1
    N = len(training_pairs)
    # print("d=", d, "\ntraining_pairs=", training_pairs)
    X = np.array([[0.0 for x_n in range(N)] for dimension in range(0, d)])
    y = np.array([0.0 for y_n in range(N)])
    for n, pair_x_y in enumerate(training_pairs):
        y_dn = pair_x_y[-1]
        y[n] = y_dn
        for dimension in range(0, d):
            x_dn = pair_x_y[dimension]
            X[dimension][n] = x_dn
            # print("X[{0}][{1}]".format(dimension, n), x_dn)
            # print("V[{0}][{1}]".format(dimension, n), V[dimension][n])
    # print('V', len(V), V)
    # S = np.where(y > 0)[0]
    # positive_y = y[S]
    # S = np.where(y < 0)[0]
    # negative_y = y[S]
    # print("positive_y", len(positive_y), len(negative_y))

    X = np.concatenate((np.ones((1, X.shape[1])), X), axis=0)

    return (X, y, N)


def save_model(w: list, output="src/algorithm/logistic_regression_content_based"):
    content = [w]
    from utils.file import write_csv
    write_csv(output,
              content,
              has_header=False,
              toStr=lambda row: "{0}".format(
                  " ".join([str(ele) for ele in row])))


def load_model(file="src/algorithm/logistic_regression_content_based"):
    with open(file) as f:
        first_line = f.readline()
        w = first_line.split(" ")
        f.close()
        return [float(wi) for wi in w]


def sigmoid(s):
    return 1/(1 + np.exp(-s))


def logistic_sigmoid_regression(X, y, w_init, eta, tol=1e-4, max_count=10000):
    w = [w_init]
    it = 0
    N = X.shape[1]
    print("N=", N)

    d = X.shape[0]
    print("d=", d)
    print("y.shape", y.shape[0])
    count = 0
    check_w_after = 20
    while count < max_count:
        # mix data
        # lấy thứ tự của từng phần tử mà không đổi chỗ
        # của từng phần tử trong danh sách
        mix_id = np.random.permutation(N)
        for i in mix_id:
            # if (i == 0):
            #     print("X", X)
            # lấy từng phần tử theo cột i tạo thành 1 list
            # xếp lại theo [[dòng 1 cột i],..,[dòng d cột i]]
            xi = X[:, i].reshape(d, 1)
            # if (i == 0):
            #     print("xi", xi)
            yi = y[i]
            zi = sigmoid(np.dot(w[-1].T, xi))
            w_new = w[-1] + eta*(yi - zi)*xi
            count += 1
            # stopping criteria
            if count % check_w_after == 0:
                if np.linalg.norm(w_new - w[-check_w_after]) < tol:
                    return w
            w.append(w_new)
    return w


def run(training_pairs):

    (X, y, N) = prepare_training_data(training_pairs)
    eta = .05

    # real dimension
    d = X.shape[0]
    w_init = np.random.randn(d, 1)
    # print("w_init=", w_init)

    w = logistic_sigmoid_regression(X, y, w_init, eta)
    w = w[-1]
    w = w[:, 0]
    save_model(w)
    w = load_model()
    print("w=", w)
