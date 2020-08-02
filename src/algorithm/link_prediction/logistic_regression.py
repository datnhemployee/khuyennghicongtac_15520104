from __future__ import division, print_function, unicode_literals
import numpy as np


_output_lg = "src/algorithm/model_link_lg"


def run(graph, output=_output_lg):
    def predict() -> list:
        w = load_model()
        query = """
            CALL {
                MATCH (a:Author)-[r:Y_POS]->(b:Author)
                WHERE NOT EXISTS(r.learn)
                RETURN DISTINCT a, 
                    b, 
                    r.common_neighbor AS common_neighbor,
                    r.adamic_adar AS adamic_adar,
                    r.jaccard_coefficient AS jaccard_coefficient,
                    r.shortest_path AS shortest_path,
                    r.katz AS katz
                UNION
                MATCH (a:Author)-[r:Y_NEG]->(b:Author)
                WHERE NOT EXISTS(r.learn)
                RETURN DISTINCT a, 
                    b, 
                    r.common_neighbor AS common_neighbor,
                    r.adamic_adar AS adamic_adar,
                    r.jaccard_coefficient AS jaccard_coefficient,
                    r.shortest_path AS shortest_path,
                    r.katz AS katz
            }
            RETURN a.author_id AS a, 
                b.author_id AS b,
                common_neighbor,
                adamic_adar,
                jaccard_coefficient,
                shortest_path,
                katz
        """
        result = graph.run(query)
        result = list(result)

        recommendation_list = [
            [0, 0, 0] for row in result]

        for idx, row in enumerate(result):
            vector = np.array([
                result[idx][2],
                result[idx][3],
                result[idx][4],
                result[idx][5],
                result[idx][6]
            ])
            predict_y = sigmoid(np.dot(w.T, vector))

            recommendation_list[idx][0] = result[idx][0]
            recommendation_list[idx][1] = result[idx][1]
            recommendation_list[idx][2] = predict_y

        return recommendation_list

    def toDB(recommendation_list: list):
        query = """
            MATCH (:Author)-[r:LINK_LG_POS]-(:Author)
            DELETE r
        """
        graph.run(query)
        query = """
            MATCH (:Author)-[r:LINK_LG_NEG]-(:Author)
            DELETE r
        """
        graph.run(query)
        query_pos = """
            MATCH (a:Author),(b:Author)
            WHERE a.author_id=$a AND b.author_id=$b 
            CREATE (a)-[:LINK_LG_POS { score: $score }]->(b)
        """
        query_neg = """
            MATCH (a:Author),(b:Author)
            WHERE a.author_id=$a AND b.author_id=$b 
            CREATE (a)-[:LINK_LG_NEG { score: $score }]->(b)
        """
        for recommendation in recommendation_list:
            predict_y = recommendation[2]
            a = recommendation[0]
            b = recommendation[1]
            if (predict_y > 0.5):
                graph.run(query_pos, parameters={
                          'score': predict_y, 'a': a, 'b': b})
            else:
                graph.run(query_neg, parameters={
                          'score': predict_y, 'a': a, 'b': b})

    training_pair = get_training_pair(graph)
    train(training_pair)

    recommendations = predict()
    toDB(recommendations)


def valuate(graph):

    true_positive = 0
    false_positive = 1
    false_negative = 0

    precision = 0
    recall = 0
    f_measure = 0

    query = """
            MATCH (a:Author)-[r:Y_POS]-(lily:Author)
            WHERE EXISTS((a)-[:LINK_LG_POS]-(lily))
            RETURN COUNT(r) AS tp
            """
    for idx, row in enumerate(graph.run(query,)):
        true_positive = row[0]

    # fp: Số liên kết không đúng nhưng vẫn được tiên đoán
    # lấy số liên kết cần tiên đoán tại mỗi nút
    # xem trong topk' với k'<5 và k'=số liên kết cần tiên đoán tại mỗi nút,
    # có bao nhiêu tiên đoán sai
    query = """
            MATCH (a:Author)-[r:LINK_LG_POS]-(lily:Author)
            WHERE NOT EXISTS((a)-[:Y_POS]-(lily))
            RETURN COUNT(r) AS fp
            """
    for idx, row in enumerate(graph.run(query,)):
        false_positive = row[0]

    # fn: Số liên kết thật sự đúng nhưng không được tiên đoán
    # 1.Tìm số liên kết cần tiên đoán tại mỗi nút num_col,  num_col <= 5
    # 2.Số liên kết thật sự đúng và được chưa tiên đoán trong giới hạn num_col =
    #   num_col - Số liên kết thật sự đúng và được tiên đoán trong giới hạn num_col
    query = """
            MATCH (a:Author)-[r:Y_POS]-(lily:Author)
            WHERE NOT EXISTS((a)-[:LINK_LG_POS]-(lily))
            RETURN COUNT(r) AS tp
            """
    for idx, row in enumerate(graph.run(query,)):
        false_negative = row[0]

    precision = true_positive * 1.0/(true_positive + false_positive)
    recall = true_positive * 1.0/(true_positive + false_negative)
    f_measure = 2*precision * recall * 1.0/(precision + recall)
    print("precision", precision, "recall", recall, "f_measure", f_measure)
    return (precision, recall, f_measure)


def add_common_neighbor(graph):
    print("add_common_neighbor: Start")
    query = """
            MATCH (:Author)-[r:Y_POS|Y_NEG]-(:Author)
            SET r.common_neighbor = 0
          """
    graph.run(query)
    query = """
            // Get user pairs and count of distinct products that they have both purchased
            MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
            WHERE bob <> lily
                AND neighbor.prior=TRUE
                AND bob.prior = TRUE
                AND lily.prior = TRUE
                AND (EXISTS((bob)-[:Y_POS]-(lily)) OR EXISTS((bob)-[:Y_NEG]-(lily)))
            WITH DISTINCT bob, lily, COUNT(DISTINCT neighbor) AS common_neighbor

            MATCH (bob)-[r:Y_POS|Y_NEG]-(lily)
            SET r.common_neighbor = common_neighbor
            """
    graph.run(query)
    print("add_common_neighbor: End")


def add_adamic_adar(graph):
    print("add_adamic_adar: Start")
    query = """
            MATCH (:Author)-[r:Y_POS|Y_NEG]-(:Author)
            SET r.adamic_adar = 0
          """
    graph.run(query)
    query = """
            // Get user pairs and count of distinct products that they have both purchased
            MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
            WHERE bob <> lily
                AND neighbor.prior=TRUE
                AND bob.prior = TRUE
                AND lily.prior = TRUE
                AND (EXISTS((bob)-[:Y_POS]-(lily)) OR EXISTS((bob)-[:Y_NEG]-(lily)))
            WITH  bob, lily, neighbor, SIZE((neighbor)-[:COLLABORATE_PRIOR]-(:Author)) AS neighbor_neigh
            WITH  bob, lily, neighbor, 1.0/LOG(neighbor_neigh) AS inner_index
            WITH  bob, lily, SUM(inner_index) AS adamic_adar

            MATCH (bob)-[r:Y_POS|Y_NEG]-(lily)
            SET r.adamic_adar = adamic_adar
            """
    graph.run(query)
    print("add_adamic_adar: End")


def add_jaccard_coefficient(graph):
    print("add_jaccard_coefficient: Start")
    query = """
            MATCH (:Author)-[r:Y_POS|Y_NEG]-(:Author)
            SET r.jaccard_coefficient = 0.0
          """
    graph.run(query)
    query = """
            // Get user pairs and count of distinct products that they have both purchased
            MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
            WHERE bob <> lily
                AND neighbor.prior=TRUE
                AND bob.prior = TRUE
                AND lily.prior = TRUE
                AND (EXISTS((bob)-[:Y_POS]-(lily)) OR EXISTS((bob)-[:Y_NEG]-(lily)))
            WITH  bob,
                lily,
                COUNT(DISTINCT neighbor) AS intersection_count,
            SIZE((bob)-[:COLLABORATE_PRIOR]-(:Author)) AS num_neighBob,
            SIZE((lily)-[:COLLABORATE_PRIOR]-(:Author)) AS num_neighLily

            WITH bob, lily, intersection_count, (num_neighBob+ num_neighLily) - intersection_count AS union_count

            WITH bob, lily, (intersection_count*1.0/union_count) as jaccard_coefficient

            MATCH (bob)-[r:Y_POS|Y_NEG]-(lily)
            SET r.jaccard_coefficient = jaccard_coefficient
            """
    graph.run(query)
    print("add_jaccard_coefficient: End")


def add_shortest_path(graph):
    print("add_shortest_path: Start")
    query = """
            MATCH (:Author)-[r:Y_POS|Y_NEG]-(:Author)
            SET r.shortest_path=0
          """
    graph.run(query)
    query = """
            // Get user pairs and count of distinct products that they have both purchased
            CALL {
                MATCH (bob:Author)-[r:Y_POS|Y_NEG]-(lily:Author)
                RETURN  DISTINCT r, WHEN EXISTS((bob)-[:COLLABORATE_PRIOR]-(lily)) WHEN TRUE THEN 1 ELSE 0 AS shortest_path
                UNION
                MATCH (bob:Author)-[r:Y_POS|Y_NEG]-(lily:Author)
                RETURN  DISTINCT r, WHEN EXISTS((bob)-[:COLLABORATE_PRIOR*2]-(lily)) WHEN TRUE THEN 2 ELSE 0 AS shortest_path
                UNION
                MATCH (bob:Author)-[r:Y_POS|Y_NEG]-(lily:Author)
                RETURN  DISTINCT r, WHEN EXISTS((bob)-[:COLLABORATE_PRIOR*3]-(lily)) WHEN TRUE THEN 3 ELSE 0 AS shortest_path
            }
            WITH  DISTINCT r, shortest_path

            ORDER BY shortest_path ASC
            WITH  DISTINCT r, COLLECT(shortest_path) AS shortest_path
            WITH  DISTINCT r, shortest_path[0] AS shortest_path
            SET r.shortest_path = shortest_path
            """
    graph.run(query)
    print("add_shortest_path: End")


def add_katz(graph, beta=0.85):
    print("add_katz: Start")
    query = """
            MATCH (:Author)-[r:Y_POS|Y_NEG]-(:Author)
            SET r.katz=0
          """
    graph.run(query)
    query = """
            MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
            WHERE bob <> lily
                AND neighbor.prior=TRUE
                AND bob.prior = TRUE
                AND lily.prior = TRUE
                AND (EXISTS((bob)-[:Y_POS]-(lily)) OR EXISTS((bob)-[:Y_NEG]-(lily)))
            WITH DISTINCT bob,
                lily,
                (SIZE((bob)-[:COLLABORATE_PRIOR*2]-(lily)) * $beta * $beta +
                SIZE((bob)-[:COLLABORATE_PRIOR*3]-(lily)) * $beta * $beta * $beta) AS katz

            WITH bob, lily, katz

            MATCH (bob)-[r:Y_POS|Y_NEG]-(lily)
            SET r.katz = katz
            """
    graph.run(query, parameters={'beta': beta})
    print("add_katz: End")


def get_training_pair(graph) -> list:
    print("create_training_pair: Start")
    """
        Thêm số đo vào tất cả các link cần dự đoán
    """
    add_adamic_adar(graph)
    add_common_neighbor(graph)
    add_jaccard_coefficient(graph)
    add_katz(graph)
    add_shortest_path(graph)

    """
        Lấy 50% mẫu dương và âm
    """
    query = """
        CALL {
                MATCH (a:Author)-[r:Y_POS]->(b:Author)
                WHERE r.learn=TRUE
                RETURN DISTINCT r.common_neighbor AS common_neighbor,
                    r.adamic_adar AS adamic_adar,
                    r.jaccard_coefficient AS jaccard_coefficient,
                    r.shortest_path AS shortest_path,
                    r.katz AS katz,
                    1 AS existed
                UNION
                MATCH (a:Author)-[r:Y_NEG]->(b:Author)
                WHERE r.learn=TRUE
                RETURN DISTINCT r.common_neighbor AS common_neighbor,
                    r.adamic_adar AS adamic_adar,
                    r.jaccard_coefficient AS jaccard_coefficient,
                    r.shortest_path AS shortest_path,
                    r.katz AS katz, 
                    0 AS existed
            }
        RETURN DISTINCT common_neighbor,
            adamic_adar,
            jaccard_coefficient,
            shortest_path,
            katz,
            existed
    """
    toList = graph.run(query)
    toList = list(toList)
    result = [[0.0, 0.0, 0.0, 0.0, 0.0, -1]
              for idx in range(0, len(toList), 1)]
    for idx, row in enumerate(toList):
        for dimension, value in enumerate(row):
            result[idx][dimension] = value

    # print("result=", result)
    print("create_training_pair: End")
    return result


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

    return (X, y, N)


def save_model(w: list, output=_output_lg):
    content = [w]
    from utils.file import write_csv
    write_csv(output,
              content,
              has_header=False,
              toStr=lambda row: "{0}".format(
                  " ".join([str(ele) for ele in row])))


def load_model(file=_output_lg):
    with open(file) as f:
        first_line = f.readline()
        w = first_line.split(" ")
        f.close()
        return np.array([float(wi) for wi in w])


def train(training_pairs: list):

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
