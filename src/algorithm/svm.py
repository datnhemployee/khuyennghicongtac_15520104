import numpy as np
import matplotlib.pyplot as plt
from cvxopt import matrix, solvers
from scipy.spatial.distance import cdist


def prepare_training_data(
    training_pairs: list
) -> (list, list, list, int):
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
    V = np.array([[0.0 for v_n in range(N)] for dimension in range(0, d)])
    y = np.array([[0.0 for y_n in range(N)]])
    for n, pair_x_y in enumerate(training_pairs):
        y_dn = pair_x_y[-1]
        y[0][n] = y_dn
        for dimension in range(0, d):
            x_dn = pair_x_y[dimension]
            X[dimension][n] = x_dn
            # print("X[{0}][{1}]".format(dimension, n), x_dn)
            V[dimension][n] = x_dn * y_dn
            # print("V[{0}][{1}]".format(dimension, n), V[dimension][n])
    # print('V', len(V), V)
    # S = np.where(y > 0)[0]
    # positive_y = y[S]
    # S = np.where(y < 0)[0]
    # negative_y = y[S]
    # print("positive_y", len(positive_y), len(negative_y))

    return (X, V, y, N)


def is_positive_semi_infinite(matrix, tol=1e-8):
    E = np.linalg.eigvalsh(matrix)
    return np.all(E > -tol)


def train(X, V, y, N):

    # print("N={0}".format(N))
    K = matrix(V.T.dot(V))

    if (not is_positive_semi_infinite(K)):
        raise "K is not a positive semi-infinite matrix!!"

    # print("K={0}".format(K))
    # print('K', len(K), K[0])
    p = matrix(-np.ones((N, 1)))
    # print('p', len(p))
    # print('p={0}'.format(p))

    G = matrix(-np.eye(N))
    # print('G', len(G))
    h = matrix(np.zeros((N, 1)))
    # print('h', len(h))

    A = matrix(y)
    b = matrix(np.zeros((1, 1)))
    # print('G', len(A))
    print("learning,...")
    sol = solvers.qp(P=K, q=p, G=G, h=h, A=A, b=b)

    l = np.array(sol['x'])
    # print('lamda={0}'.format(l))

    # Vì sai số tính toán nên giá trị trị thực khác 0
    # Cách tìm giá trị thực = giá trị của các support vector > 1e-6 = 10^-6
    epsilon = 1e-6
    # Tập S={vị trí của các lambda khác 0}
    S = np.where(l > epsilon)[0]
    # print('S={0}'.format(S))

    # Ma trận VS={vị trí của các support vectơ có lambda khác 0}
    VS = V[:, S]
    # print('VS={0}'.format(VS))
    # Ma trận XS={vị trí của các vectơ có lambda khác 0}
    XS = X[:, S]
    # print('XS={0}'.format(XS))
    # Ma trận yS={vị trí của các nhãn có lambda khác 0}
    yS = y[:, S]
    # print('yS={0}'.format(yS))
    # Ma trận lS={tập chứa lambda khác 0}
    lS = l[S]
    # print('lS={0}'.format(lS))

    # w = Ma trận VS.dot(lS)
    w = VS.dot(lS)
    # b = np.mean = Xích ma của tập S(y_n - w.T.dot(x_n)) * 1/N_S
    b = np.mean(yS.T - w.T.dot(XS))

    return w.T, b

# def train(X, V, y, N):
#     from sklearn.svm import SVC

#     y1 = y.reshape((N,))
#     X1 = X.T  # each sample is one row
#     print("learning,...")
#     clf = SVC(kernel='linear', C=1e5)  # just a big number

#     clf.fit(X1, y1)

#     w = clf.coef_
#     b = clf.intercept_

#     return w, b


def run(
    training_pairs: list
) -> (list, int):
    (X, V, y, N) = prepare_training_data(training_pairs=training_pairs)
    (w, b) = train(X, V, y, N)
    return (w, b)


def create_positive_common_neighbor_link(graph):
    print("create_positive_common_neighbor_link: Start")
    query = """
            MATCH (a:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]-(b:Author)
            WHERE a.test=TRUE AND
                b.test=TRUE AND
                b <> a AND
                r.model="svm"
            DELETE r
          """
    graph.run(query)
    query = """
            // Get user pairs and count of distinct products that they have both purchased
            MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
            WHERE bob <> lily
                AND neighbor.test=TRUE
                AND bob.test = TRUE
                AND lily.test = TRUE
                AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
                AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
            WITH DISTINCT bob, lily, COUNT(DISTINCT neighbor) AS common_neighbor_count
            CREATE (bob)-[:COMMON_NEIGHBOR_RECOMMEND { score: common_neighbor_count, model:"svm" }]->(lily)
            """
    graph.run(query)
    print("create_positive_common_neighbor_link: End")


def create_negative_common_neighbor_link(graph):
    print("create_negative_common_neighbor_link: Start")
    query = """
            MATCH (a:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]-(b:Author)
            WHERE a.test=TRUE AND
                b.test=TRUE AND
                b <> a AND
                r.model="svm" AND
                r.negative=TRUE
            DELETE r
          """
    graph.run(query)
    query = """
            // Lấy số lượng positive link theo từng bob
            MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]->(lily:Author)
            WHERE bob.test=TRUE AND
                lily.test=TRUE AND
                bob<>lily AND
                r.model="svm" AND
                NOT EXISTS(r.negative)
            WITH bob,
                COLLECT(DISTINCT lily) AS collect_positive
            WITH bob,
                SIZE(collect_positive) AS num_positive

            // Lấy negative sample theo từng bob
            MATCH (bob)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
            WHERE bob <> lily
                AND neighbor.test=TRUE
                AND lily.test = TRUE
                AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
                AND NOT EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
            WITH DISTINCT bob,
                lily,
                COUNT(DISTINCT neighbor) AS common_neighbor_count,
                num_positive

            // Lấy negative sample với số lượng theo positive theo từng bob
            ORDER BY common_neighbor_count, lily.author_id
            WITH bob,
                COLLECT(lily)[0..num_positive] AS collect_negative,
                COLLECT(common_neighbor_count)[0..num_positive] AS collect_negative_common_neighbor_count,
                RANGE(0,num_positive,1) AS collect_idx
            UNWIND collect_idx AS idx
            WITH bob,
                collect_negative[idx] AS lily,
                collect_negative_common_neighbor_count[idx] AS common_neighbor_count
            WHERE NOT lily IS NULL
            CREATE (bob)-[:COMMON_NEIGHBOR_RECOMMEND {
                score: common_neighbor_count,
                model:"svm",
                negative:TRUE }]->(lily)
            """
    graph.run(query)
    print("create_negative_common_neighbor_link: End")


def create_positive_adamic_adar_link(graph):
    print("create_positive_adamic_adar_link: Start")
    query = """
          MATCH (a:Author)-[r:ADAMIC_ADAR_RECOMMEND]-(b:Author)
          WHERE a.test=TRUE
            AND b.test=TRUE
            AND b <> a
            AND r.model="svm"
          DELETE r
          """
    graph.run(query)

    query = """
          MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
          WHERE bob <> lily
            AND neighbor.test =true
            AND bob.test =true
            AND lily.test =true
            AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
            AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
          WITH  bob, lily, neighbor, SIZE((neighbor)-[:COLLABORATE_PRIOR]-(:Author)) AS neighbor_neigh
          WITH  bob, lily, neighbor, 1.0/LOG(neighbor_neigh) AS inner_index
          WITH  bob, lily, SUM(inner_index) AS adamic_adar_index
          CREATE (bob)-[:ADAMIC_ADAR_RECOMMEND { score:adamic_adar_index, model:"svm" }]->(lily)
          """
    graph.run(query)
    print("create_positive_adamic_adar_link: End")


def create_negative_adamic_adar_link(graph):
    print("create_negative_adamic_adar_link: Start")
    query = """
          MATCH (a:Author)-[r:ADAMIC_ADAR_RECOMMEND]-(b:Author)
          WHERE a.test=TRUE
            AND b.test=TRUE
            AND b <> a
            AND r.model="svm"
            AND r.negative=TRUE
          DELETE r
          """
    graph.run(query)

    query = """
        // Lấy số lượng negative common neighbor link theo từng bob
        MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]->(lily:Author)
        WHERE bob.test=TRUE AND
            lily.test=TRUE AND
            bob<>lily AND
            r.model="svm" AND
            r.negative=TRUE
        WITH bob, lily

        MATCH (bob)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily)
        WHERE bob <> lily
            AND neighbor.test =true
            AND bob.test =true
            AND lily.test =true
            AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
            AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
        WITH  bob, lily, neighbor, SIZE((neighbor)-[:COLLABORATE_PRIOR]-(:Author)) AS neighbor_neigh
        WITH  bob, lily, neighbor, 1.0/LOG(neighbor_neigh) AS inner_index
        WITH  bob, lily, SUM(inner_index) AS adamic_adar_index
        CREATE (bob)-[:ADAMIC_ADAR_RECOMMEND { score:adamic_adar_index, model:"svm", negative:TRUE }]->(lily)
        """
    graph.run(query)
    print("create_negative_adamic_adar_link: End")


def create_positive_jaccard_coefficient_link(graph):
    print("create_positive_jaccard_coefficient_link: Start")
    query = """
          MATCH (a:Author)-[r:JACCARD_COEFFICIENT_RECOMMEND]-(b:Author)
          WHERE a.test=TRUE
            AND b.test=TRUE
            AND b <> a
            AND r.model="svm"
          DELETE r
          """
    graph.run(query)

    query = """
          MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
          WHERE neighbor.test=TRUE
            AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
            AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
          WITH  bob,
            lily,
            COUNT(DISTINCT neighbor) AS intersection_count,
            SIZE((bob)-[:COLLABORATE_PRIOR]-(:Author)) AS num_neighBob,
            SIZE((lily)-[:COLLABORATE_PRIOR]-(:Author)) AS num_neighLily

          WITH bob, lily, intersection_count, (num_neighBob+ num_neighLily) - intersection_count AS union_count

          WITH bob, lily, (intersection_count*1.0/union_count) as jaccard_index
          CREATE (bob)-[:JACCARD_COEFFICIENT_RECOMMEND { score:jaccard_index, model:"svm" }]->(lily)
          """
    graph.run(query)
    print("create_positive_jaccard_coefficient_link: End")


def create_negative_jaccard_coefficient_link(graph):
    print("create_negative_jaccard_coefficient_link: Start")
    query = """
          MATCH (a:Author)-[r:JACCARD_COEFFICIENT_RECOMMEND]-(b:Author)
          WHERE a.test=TRUE
            AND b.test=TRUE
            AND b <> a
            AND r.model="svm" AND
            r.negative=TRUE
          DELETE r
          """
    graph.run(query)

    query = """
        // Lấy số lượng negative common neighbor link theo từng bob
        MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]->(lily:Author)
        WHERE bob.test=TRUE AND
            lily.test=TRUE AND
            bob<>lily AND
            r.model="svm" AND
            r.negative=TRUE
        WITH bob, lily

        MATCH (bob)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily)
        WHERE neighbor.test=TRUE
            AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
            AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
        WITH  bob,
            lily,
            COUNT(DISTINCT neighbor) AS intersection_count,
            SIZE((bob)-[:COLLABORATE_PRIOR]-(:Author)) AS num_neighBob,
            SIZE((lily)-[:COLLABORATE_PRIOR]-(:Author)) AS num_neighLily

        WITH bob, lily, intersection_count, (num_neighBob+ num_neighLily) - intersection_count AS union_count

        WITH bob, lily, (intersection_count*1.0/union_count) as jaccard_index
        CREATE (bob)-[:JACCARD_COEFFICIENT_RECOMMEND { score:jaccard_index, model:"svm", negative:TRUE }]->(lily)
        """
    graph.run(query)
    print("create_negative_jaccard_coefficient_link: End")


def create_positive_shortest_path_link(graph):
    print("create_positive_shortest_path_link: Start")
    query = """
          MATCH (a:Author)-[r:SHORTEST_PATH_RECOMMEND]-(b:Author)
          WHERE a.test=TRUE AND
            b.test=TRUE AND
            b <> a AND
            r.model="svm"
          DELETE r
          """
    graph.run(query)

    query = """
            CALL {
                MATCH (bob:Author)-[:COLLABORATE_PRIOR*2]-(lily:Author)
                WHERE bob <> lily
                    AND bob.test =true
                    AND lily.test =true
                    AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
                    AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
                RETURN DISTINCT  bob, lily, 2 AS length
                UNION
                MATCH (bob:Author)-[:COLLABORATE_PRIOR*3]-(lily:Author)
                WHERE bob <> lily
                    AND bob.test =true
                    AND lily.test =true
                    AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
                    AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
                RETURN DISTINCT bob, lily, 3 AS length
                UNION
                MATCH (bob:Author)-[:COLLABORATE_PRIOR*4]-(lily:Author)
                WHERE bob <> lily
                    AND bob.test =true
                    AND lily.test =true
                    AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
                    AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
                RETURN DISTINCT bob, lily, 4 AS length
            }
            WITH DISTINCT bob, lily, 1.0/length AS shortest_path_index
            CREATE(bob)-[:SHORTEST_PATH_RECOMMEND { score:shortest_path_index,model:"svm" }]->(lily)
          """
    graph.run(query)
    print("create_positive_shortest_path_link: End")


def create_negative_shortest_path_link(graph):
    print("create_negative_shortest_path_link: Start")
    query = """
          MATCH (a:Author)-[r:SHORTEST_PATH_RECOMMEND]-(b:Author)
          WHERE a.test=TRUE AND
            b.test=TRUE AND
            b <> a AND
            r.model="svm" AND
            r.negative=TRUE
          DELETE r
          """
    graph.run(query)

    query = """
        CALL {
            MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]->(lily:Author)
            WHERE bob.test=TRUE AND
                lily.test=TRUE AND
                bob<>lily AND
                r.model="svm" AND
                r.negative=TRUE AND
                NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily)) AND
                EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
            RETURN DISTINCT  bob,
                lily,
                CASE EXISTS((bob)-[:COLLABORATE_PRIOR*2]-(lily))
                WHEN TRUE
                THEN 1.0/2
                ELSE 0
                END AS shortest_path_index
            UNION
            MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]->(lily:Author)
            WHERE bob.test=TRUE AND
                lily.test=TRUE AND
                bob<>lily AND
                r.model="svm" AND
                r.negative=TRUE AND
                NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily)) AND
                EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
            RETURN DISTINCT  bob,
                lily,
                CASE EXISTS((bob)-[:COLLABORATE_PRIOR*3]-(lily))
                WHEN TRUE
                THEN 1.0/3
                ELSE 0
                END AS shortest_path_index
            UNION
            MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]->(lily:Author)
            WHERE bob.test=TRUE AND
                lily.test=TRUE AND
                bob<>lily AND
                r.model="svm" AND
                r.negative=TRUE AND
                NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily)) AND
                EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
            RETURN DISTINCT  bob,
                lily,
                CASE EXISTS((bob)-[:COLLABORATE_PRIOR*4]-(lily))
                WHEN TRUE
                THEN 1.0/4
                ELSE 0
                END AS shortest_path_index
        }
        WITH DISTINCT bob, lily, shortest_path_index

        ORDER BY shortest_path_index, lily.author_id
        WITH DISTINCT bob, lily, COLLECT(shortest_path_index) AS shortest_path_index_list
        WITH DISTINCT bob, lily, shortest_path_index_list[0] AS shortest_path_index
        CREATE(bob)-[:SHORTEST_PATH_RECOMMEND { score:shortest_path_index, model:"svm", negative:TRUE }]->(lily)
    """
    graph.run(query)
    print("create_negative_shortest_path_link: End")


def create_positive_katz_link(graph, beta=0.85):
    print("create_positive_katz_link: Start")
    query = """
          MATCH (a:Author)-[r:KAZT_RECOMMEND]-(b:Author)
          WHERE a.test=TRUE AND
            b.test=TRUE AND
            b <> a AND
            r.model="svm"
          DELETE r
          """
    graph.run(query)

    query = """
        MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
        WHERE bob <> lily
            AND neighbor.test=TRUE
            AND bob.test =TRUE
            AND lily.test =TRUE
            AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
            AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
        WITH DISTINCT bob,
            lily,
            (SIZE((bob)-[:COLLABORATE_PRIOR*2]-(lily)) * $beta * $beta +
            SIZE((bob)-[:COLLABORATE_PRIOR*3]-(lily)) * $beta * $beta * $beta) AS kazt_index

        WITH bob, lily, kazt_index

        CREATE(bob)-[:KAZT_RECOMMEND { score:kazt_index, model:"svm" }]->(lily)
        """

    graph.run(query, parameters={'beta': beta})
    print("create_positive_katz_link: End")


def create_negative_katz_link(graph, beta=0.85):
    print("create_negative_katz_link: Start")
    query = """
          MATCH (a:Author)-[r:KAZT_RECOMMEND]-(b:Author)
          WHERE a.test=TRUE AND
            b.test=TRUE AND
            b <> a AND
            r.model="svm" AND
            r.negative=TRUE
          DELETE r
          """
    graph.run(query)

    query = """
        // Lấy số lượng negative common neighbor link theo từng bob
        MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]->(lily:Author)
        WHERE bob.test=TRUE AND
            lily.test=TRUE AND
            bob<>lily AND
            r.model="svm" AND
            r.negative=TRUE
        WITH bob, lily

        MATCH (bob)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily)
        WHERE neighbor.test=TRUE AND
            NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
            AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
        WITH DISTINCT bob,
            lily,
            (SIZE((bob)-[:COLLABORATE_PRIOR*2]-(lily)) * $beta * $beta +
            SIZE((bob)-[:COLLABORATE_PRIOR*3]-(lily)) * $beta * $beta * $beta) AS kazt_index

        WITH bob, lily, kazt_index
        CREATE(bob)-[:KAZT_RECOMMEND { score:kazt_index, model:"svm", negative:TRUE }]->(lily)
        """

    graph.run(query, parameters={'beta': beta})
    print("create_negative_katz_link: End")


def prepare_training_vectors_link_prediction(graph):
    print("prepare_training_vectors_link_prediction: Start")
    """
    Tạo svm training data từ tập label và data
    """
    query = """
        MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND|ADAMIC_ADAR_RECOMMEND|JACCARD_COEFFICIENT_RECOMMEND|KAZT_RECOMMEND|SHORTEST_PATH_RECOMMEND]->(lily:Author)
        WHERE bob.test=TRUE AND
            lily.test=TRUE AND
            lily <> bob AND
            r.model="svm"
        WITH bob,
            lily,
            CASE TYPE(r) WHEN "COMMON_NEIGHBOR_RECOMMEND" THEN r.score ELSE 0 END AS common_neighbor,
            CASE TYPE(r) WHEN "ADAMIC_ADAR_RECOMMEND" THEN r.score ELSE 0 END AS adamic_adar,
            CASE TYPE(r) WHEN "JACCARD_COEFFICIENT_RECOMMEND" THEN r.score ELSE 0 END AS jaccard,
            CASE TYPE(r) WHEN "KAZT_RECOMMEND" THEN r.score ELSE 0 END AS katz,
            CASE TYPE(r) WHEN "SHORTEST_PATH_RECOMMEND" THEN r.score ELSE 0 END AS shortest,
            EXISTS(r.negative) AS negative
        WITH bob,
            lily,
            SUM(common_neighbor) AS common_neighbor,
            SUM(adamic_adar) AS adamic_adar,
            SUM(jaccard) AS jaccard,
            SUM(katz) AS katz,
            SUM(shortest) AS shortest,
            COLLECT(negative) AS negative
        WITH bob,
            lily,
            common_neighbor,
            adamic_adar,
            jaccard,
            katz,
            shortest,
            negative[0] AS negative
        WITH bob,
            lily,
            common_neighbor,
            adamic_adar,
            jaccard,
            katz,
            shortest,
            CASE negative WHEN TRUE THEN -1 ELSE 1 END AS existed
        RETURN DISTINCT common_neighbor,
            adamic_adar,
            jaccard,
            katz,
            shortest,
            existed
    """
    toList = graph.run(query)
    toList = list(toList)
    result = [[0.0, 0.0, 0.0, 0.0, 0.0, -1]
              for idx in range(0, len(toList), 1)]
    for idx, row in enumerate(toList):
        for dimension, value in enumerate(row):
            result[idx][dimension] = row[dimension]

    # print("result=", result)
    print("prepare_training_vectors_link_prediction: End")
    return result


def save_model(w, b, output):
    content = [[w.tolist()[0], b.tolist()[0]]]
    from utils.file import write_csv
    write_csv(output, content, "w|b", toStr=lambda row: "[{0}]|{1}".format(
        ",".join([str(ele) for ele in row[0]]), row[1]))


def run_predict_link(graph):
    print("run_predict_link: Start")
    """
    Tạo positive samples từ tập label và data
    """
    create_positive_common_neighbor_link(graph)
    create_positive_adamic_adar_link(graph)
    create_positive_jaccard_coefficient_link(graph)
    create_positive_katz_link(graph)
    create_positive_shortest_path_link(graph)
    """
    Tạo negative samples từ tập label và data
    """
    create_negative_common_neighbor_link(graph)
    create_negative_adamic_adar_link(graph)
    create_negative_jaccard_coefficient_link(graph)
    create_negative_katz_link(graph)
    create_negative_shortest_path_link(graph)
    """
    Tạo svm training data từ tập label và data
    """
    result = prepare_training_vectors_link_prediction(graph)
    (X, V, y, N) = prepare_training_data(result)
    (w, b) = train(X, V, y, N)
    print("run_predict_link: End")
    save_model(w, b, "svm_link_prediction.csv")


def predict_link(graph):
    query = """

    """
