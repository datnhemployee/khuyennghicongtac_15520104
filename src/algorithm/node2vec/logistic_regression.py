from __future__ import division, print_function, unicode_literals
import numpy as np

_emb_file = "src/algorithm/emb_node2vec_lg"
_input_graph = "src/algorithm/graph_node2vec_lg"
_output_lg = "src/algorithm/model_node2vec_lg"


def run(
    graph,
    input_graph=_input_graph,
    output=_emb_file,
    operator="average"
):
    def create_graph(graph, input_graph):
        query = """
            MATCH (a:Author)-[r:COLLABORATE_PRIOR]->(b:Author)
            WHERE a.prior=TRUE AND b.prior=TRUE
            RETURN DISTINCT a.author_id AS a, b.author_id AS b
        """
        result = graph.run(query)
        result = list(result)
        links = [[0, 0] for l in result]
        for idx, l in enumerate(result):
            links[idx][0] = l[0]
            links[idx][1] = l[1]

        from utils.file import write_csv
        write_csv(input_graph, links, has_header=False,
                  toStr=lambda row: "{0} {1}\n".format(row[0], row[1]))

    def prepare_training_pair_link_label() -> list:
        '''
            Lấy tập chứa các cặp (x,y) gồm 50% mẫu âm và mẫu dương phục vụ cho học máy
        '''
        query = """
            CALL {
                MATCH (a:Author)-[r:Y_POS]->(b:Author)
                WHERE r.learn=TRUE
                RETURN DISTINCT a, b, 1 AS existed
                UNION
                MATCH (a:Author)-[r:Y_NEG]->(b:Author)
                WHERE r.learn=TRUE
                RETURN DISTINCT a, b, 0 AS existed
            }
            RETURN a.author_id AS a, b.author_id AS b, existed
        """
        result = graph.run(query)
        result = list(result)

        dimension = get_dimension()
        vector_label = [[0.0 for d in range(dimension + 1)] for l in result]
        model = get_node2vec()
        # print("vocab", model)
        if(operator == "average"):
            for idx, row in enumerate(result):
                start_node = model[str(row[0])]
                end_node = model[str(row[1])]
                # print("row", row[2])
                vector = (start_node + end_node) * 0.5
                vector_label[idx][-1] = row[2]
                for d, val in enumerate(vector):
                    vector_label[idx][d] = val

            return vector_label

    def predict() -> list:
        w = load_model()
        query = """
            CALL {
                MATCH (a:Author)-[r:Y_POS]->(b:Author)
                WHERE NOT EXISTS(r.learn)
                RETURN DISTINCT a, b, 1 AS existed
                UNION
                MATCH (a:Author)-[r:Y_NEG]->(b:Author)
                WHERE NOT EXISTS(r.learn)
                RETURN DISTINCT a, b, 0 AS existed
            }
            RETURN a.author_id AS a, b.author_id AS b
        """
        result = graph.run(query)
        result = list(result)
        dimension = get_dimension()

        recommendation_list = [
            [0, 0, 0] for row in result]

        node2vec_model = get_node2vec()

        for idx, row in enumerate(result):
            start_node = node2vec_model[str(row[0])]
            end_node = node2vec_model[str(row[1])]
            # print("row", row[2])
            vector = (start_node + end_node) * 0.5
            predict_y = sigmoid(np.dot(w.T, vector))

            recommendation_list[idx][0] = result[idx][0]
            recommendation_list[idx][1] = result[idx][1]
            recommendation_list[idx][2] = predict_y

        return recommendation_list

    def toDB(recommendation_list: list):
        query = """
            MATCH (:Author)-[r:NODE2VEC_LG_POS]-(:Author)
            DELETE r
        """
        graph.run(query)
        query = """
            MATCH (:Author)-[r:NODE2VEC_LG_NEG]-(:Author)
            DELETE r
        """
        graph.run(query)
        query_pos = """
            MATCH (a:Author),(b:Author)
            WHERE a.author_id=$a AND b.author_id=$b 
            CREATE (a)-[:NODE2VEC_LG_POS { score: $score }]->(b)
        """
        query_neg = """
            MATCH (a:Author),(b:Author)
            WHERE a.author_id=$a AND b.author_id=$b 
            CREATE (a)-[:NODE2VEC_LG_NEG { score: $score }]->(b)
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

    from algorithm.node2vec.learn import run
    """
    Bước 1: Huấn luyện mô hình Node2vec cho mạng đồng tác giả [2010-2015]
    """
    run(graph, create_graph=create_graph,
        input_file=_input_graph, output=output)
    training_pair = prepare_training_pair_link_label()
    """
    Bước 2: Huấn luyện mô hình Logistic Regression cho mạng đồng tác giả 2010-2015
        tiên đoán 5 năm sau đó [2016-2020] 50%
    """
    train(training_pair)
    """
    Bước 3: Thêm vào db bằng 50% mẫu dương, âm còn lại
    """
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
            WHERE EXISTS((a)-[:NODE2VEC_LG_POS]-(lily))
            RETURN COUNT(r) AS tp
            """
    for idx, row in enumerate(graph.run(query,)):
        true_positive = row[0]

    # fp: Số liên kết không đúng nhưng vẫn được tiên đoán
    # lấy số liên kết cần tiên đoán tại mỗi nút
    # xem trong topk' với k'<5 và k'=số liên kết cần tiên đoán tại mỗi nút,
    # có bao nhiêu tiên đoán sai
    query = """
            MATCH (a:Author)-[r:NODE2VEC_LG_POS]-(lily:Author)
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
            WHERE NOT EXISTS((a)-[:NODE2VEC_LG_POS]-(lily))
            RETURN COUNT(r) AS tp
            """
    for idx, row in enumerate(graph.run(query,)):
        false_negative = row[0]

    precision = true_positive * 1.0/(true_positive + false_positive)
    recall = true_positive * 1.0/(true_positive + false_negative)
    f_measure = 2*precision * recall * 1.0/(precision + recall)
    print("precision", precision, "recall", recall, "f_measure", f_measure)
    return (precision, recall, f_measure)


def get_node2vec(emb_file=_emb_file):
    from gensim.models import KeyedVectors
    model = KeyedVectors.load_word2vec_format(emb_file)
    return model


def get_dimension(emb_file=_emb_file):
    with open(emb_file) as f:
        first_line = f.readline()
        temp = first_line.split(" ")
        f.close()
        return int(temp[1])


def get_training_pair(graph):
    query = """
        MATCH (a:Author)-[:X_PRIOR]-(b:Author)
        WHERE 
    """


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


def load_model(file=_output_lg) -> list:
    with open(file) as f:
        first_line = f.readline()
        w = first_line.split(" ")
        f.close()
        return np.array([float(wi) for wi in w])


def train(training_pairs):

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
