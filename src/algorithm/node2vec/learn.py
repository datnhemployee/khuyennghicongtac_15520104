from algorithm.node2vec.graph import Graph
import networkx as nx


# def create_input_file(graph, input_graph):
#     '''
#     Get all collaborations from Neo4j network to map to networkx.
#     '''
#     query = """
#         MATCH (a:Author)-[r:COLLABORATE_PRIOR]->(b:Author)
#         WHERE a.prior=TRUE AND b.prior=TRUE
#         RETURN DISTINCT a.author_id AS a, b.author_id AS b
#     """
#     result = graph.run(query)
#     result = list(result)
#     links = [[0, 0] for l in result]
#     for idx, l in enumerate(result):
#         links[idx][0] = l[0]
#         links[idx][1] = l[1]

#     from utils.file import write_csv
#     write_csv(input_graph, links, has_header=False,
#               toStr=lambda row: "{0} {1}\n".format(row[0], row[1]))


def read_graph(input_file, weighted=False, is_directed=False):
    '''
    Reads the input network in networkx.
    '''
    if (weighted):
        # no weights are add in graph init file
        G = nx.read_edgelist(input_file,
                             nodetype=int,
                             data=(('weight', float),),
                             create_using=nx.DiGraph())
    else:
        G = nx.read_edgelist(input_file,
                             nodetype=int,
                             create_using=nx.DiGraph())
        for edge in G.edges():
            G[edge[0]][edge[1]]['weight'] = 1

    if not is_directed:
        G = G.to_undirected()

    return G


def learn_embedding(
        output=None,
        walks=[],
        dimensions=128,
        window_size=10,
        workers=8,
        iter=1
):
    '''
    Learn embeddings by optimizing the Skipgram objective using SGD.
    '''
    from gensim.models import Word2Vec

    """
    + Bug: TypeError: object of type 'map' has no len()
    + Reason: (Python2.map()) <> (Python3.map())
        Because python2's map function is different from python3's.
        Try to modify line 86 in main.py to walks = [list(map(str, walk)) for walk in walks]
        If you run main.py with python2,it worked without modifying the code
    + Fix:
    see also: https://github.com/aditya-grover/node2vec/issues/35
    """
    walks = [list(map(str, walk)) for walk in walks]
    # print("walks", walks)
    model = Word2Vec(walks, size=dimensions, window=window_size,
                     min_count=0, sg=1, workers=workers, iter=iter)
    model.wv.save_word2vec_format(output)

    return


def run(
    graph=None,
    create_graph=create_input_file,

    input_file="src/algorithm/graph",
    weighted=False,
    is_directed=False,
    p=1,
    q=1,

    num_walks=10,
    walk_length=80,

    output="src/algorithm/emb",
    dimensions=128,
    window_size=5,
    workers=8,
    iter=1
):
    # Assumption
    # run
    # print("version:{0}".format(nx.__version__))
    create_graph(graph, input_file)
    nx_G = read_graph(input_file, weighted=weighted, is_directed=is_directed)
    G = Graph(nx_G=nx_G, is_directed=is_directed, p=p, q=q)
    """
    Chuẩn hóa trọng số cung liên kết để chuẩn bị cho việc bước
    """
    G.preprocess_transition_probs()
    walks = G.simulate_walks(num_walks=num_walks, walk_length=walk_length)
    learn_embedding(output,
                    walks,
                    dimensions, window_size, workers, iter)


def get_node2vec(emb_file="src/algorithm/emb"):
    from gensim.models import KeyedVectors
    model = KeyedVectors.load_word2vec_format(emb_file)
    return model


def get_most_similar(model, author_id: str, topn=5) -> list:
    result = model.most_similar(positive=[author_id], negative=[], topn=topn)
    return result


def predicted_link_to_db(graph, num_author=1000, K=5):

    query = """
            MATCH (:Author)-[r:NODE2VEC]-(:Author)
            DELETE r
        """
    graph.run(query)

    def predict() -> list:
        query = """
            MATCH (a:Author)
            WHERE a.test=TRUE
            RETURN DISTINCT a.author_id
        """
        model = get_node2vec()
        list_author = [{"author_id": 0, "topK": [-1 for topk in range(K)]}
                       for auth in range(num_author)]
        for idx, row in enumerate(graph.run(query)):
            author_id = row[0]
            list_author[idx]["author_id"] = author_id
            most_sim = get_most_similar(model, str(author_id), K)
            for topk, auth_id in enumerate(most_sim):
                list_author[idx]["topK"][topk-1] = int(auth_id[0])
                # print("auth_id[0]", auth_id[0])

        return list_author

    def to_db(recommendation_list: list):
        if(len(recommendation_list) == 0):
            raise "Error: No authors were found to make any prediction!!"

        query = """
            MATCH (a:Author),(b:Author)
            WHERE a.author_id=$a_id AND
                 b.author_id=$b_id
            CREATE (a)-[:NODE2VEC { top:$top }]->(b)
        """
        for idx, auth_rec in enumerate(recommendation_list):
            a_id = auth_rec["author_id"]
            for top, b_id in enumerate(auth_rec["topK"]):
                # print("a_id", a_id, "b_id", b_id)
                if (b_id > 0):
                    graph.run(query, parameters={
                              "a_id": a_id, "b_id": b_id, "top": top})

    list_author_recommendations = predict()
    to_db(list_author_recommendations)


def valuate(graph, ):

    true_positive = 0
    false_positive = 5
    false_negative = 5

    precision = 0
    recall = 0
    f_measure = 0

    """
    true_positive: Số liên kết thật sự đúng nhưng không được tiên đoán

        1.Tìm số liên kết cần tiên đoán tại mỗi nút num_col,  num_col <= 5
        2.Số liên kết thật sự đúng và được chưa tiên đoán trong giới hạn num_col =
            num_col - Số liên kết thật sự đúng và được tiên đoán trong giới hạn num_col
    """
    query = """
            MATCH (a:Author)-[r:NODE2VEC]->(lily:Author)
            WHERE lily.prior = TRUE
                AND EXISTS((a)-[:COLLABORATE_TEST]-(lily))
            RETURN COUNT(r) AS tp
            """
    for idx, row in enumerate(graph.run(query,)):
        true_positive = row[0]

    """
    false_positive: Số liên kết không đúng nhưng vẫn được tiên đoán

        + lấy số liên kết cần tiên đoán tại mỗi nút
        + xem trong topk' với k'<5 và k'=số liên kết cần tiên đoán tại mỗi nút,
            có bao nhiêu tiên đoán sai
    """
    query = """
            MATCH (a:Author)-[r:COLLABORATE_TEST]-(b:Author)
            WITH DISTINCT a, COUNT(DISTINCT b.author_id) AS num_col
            
            MATCH (a)-[r:NODE2VEC]->(lily:Author)
            WHERE lily.prior = TRUE
                AND r.top < num_col
                AND NOT EXISTS((a)-[:COLLABORATE_TEST]-(lily))
            RETURN COUNT(r) AS fp
            """
    for idx, row in enumerate(graph.run(query,)):
        false_positive = row[0]

    """
    false_negative: Số liên kết thật sự đúng nhưng không được tiên đoán

        1.Tìm số liên kết cần tiên đoán tại mỗi nút num_col,  num_col <= 5
        2.Số liên kết thật sự đúng và được chưa tiên đoán trong giới hạn num_col =
            num_col - Số liên kết thật sự đúng và được tiên đoán trong giới hạn num_col
    """
    query = """
            MATCH (a:Author)-[r:COLLABORATE_TEST]-(b:Author)
            WITH DISTINCT a, COUNT(DISTINCT b.author_id) AS num_col
            
            MATCH (a)-[r:NODE2VEC]->(lily:Author)
            WHERE lily.prior = TRUE
                AND r.top < num_col
            WITH a, CASE EXISTS((a)-[:COLLABORATE_TEST]-(lily)) WHEN TRUE THEN 1 ELSE 0 END AS existed, num_col
            WITH a, SUM(existed) AS true_positive, COLLECT(num_col) AS num_col
            WITH a, num_col[0]- true_positive AS false_negative
            RETURN SUM(false_negative) AS false_negative
            """
    for idx, row in enumerate(graph.run(query,)):
        false_negative = row[0]

    precision = true_positive * 1.0/(true_positive + false_positive)
    recall = true_positive * 1.0/(true_positive + false_negative)
    f_measure = 2*precision * recall * 1.0/(precision + recall)
    print("precision", precision, "recall", recall, "f_measure", f_measure)
    return (precision, recall, f_measure)
