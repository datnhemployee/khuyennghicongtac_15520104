# Implements user-user collaborative filtering using the following steps:
#   1. For each user pair, compute Jaccard index
#   2. For each target user, select top k neighbours based on Jaccard index
#   3. Identify products purchased by the top k neighbours that have not been purchased by the target user
#   4. Rank these products by the number of purchasing neighbours
#   5. Return the top n recommendations for each user
import numpy as np


def run(graph, neighbourhood_size=5):
    # error: py2neo.database.ClientError: SyntaxError: Type mismatch: expected Path but was List<Node> (line 18, column 25 (offset: 905))" WHERE LENGTH(neighbours) = $k // only want users with enough neighbours"
    # https://neo4j.com/docs/cypher-manual/current/functions/scalar/#functions-size
    query = """
            MATCH (:Author)-[r:COMMON_NEIGHBOR]-(:Author)
            DELETE r
          """
    graph.run(query)
    query = """
            MATCH (:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]-(:Author)
            DELETE r
          """
    graph.run(query)
    query = """
            // Get user pairs and count of distinct products that they have both purchased
            MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
            WHERE bob <> lily
            AND neighbor.prior=TRUE
            AND bob.prior = TRUE
            AND lily.prior = TRUE
            AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
            WITH  bob, lily, COUNT(DISTINCT neighbor) AS common_neighbor_count

            // Get top k neighbours based on Common Neighbor
            ORDER BY  common_neighbor_count DESC, lily.author_id
            WITH bob,
                COLLECT(lily)[0..$k] AS recommendations,
                COLLECT(common_neighbor_count)[0..$k] AS common_neighbor_count_list,
                RANGE(0,$k,1) AS coll_size
            WHERE SIZE(recommendations) = $k
                AND SIZE(common_neighbor_count_list) = $k
            UNWIND coll_size AS idx
            WITH DISTINCT bob, 
                recommendations[idx] AS friend, 
                common_neighbor_count_list[idx] AS common_neighbor_count, 
                idx AS top
            WHERE NOT friend IS NULL AND common_neighbor_count <> 0
            WITH DISTINCT bob, friend, common_neighbor_count, top + 1 AS top
            CREATE (bob)-[:COMMON_NEIGHBOR { top:top, score: common_neighbor_count }]->(friend)
            """

    graph.run(query, parameters={'k': 5})


def draw_data(training_pairs):
    from mpl_toolkits import mplot3d
    import numpy as np
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = plt.axes(projection='3d')

    for training_pair in training_pairs:
        xdata = training_pair[0]
        ydata = training_pair[1]
        zdata = training_pair[2]
        if(training_pair[3] == -1):
            ax.scatter3D(*zip([xdata, ydata, zdata]), color="b")
        else:
            ax.scatter3D(*zip([xdata, ydata, zdata]), color="r")
    plt.show()


def prepare_data_svm(graph) -> list:
    query = """
            MATCH (a:Author)-[r:COMMON_NEIGHBOR_SVM_RECOMMEND]-(b:Author)
            WHERE a.test=TRUE AND b.test=TRUE AND b <> a
            DELETE r
          """
    graph.run(query)
    query = """
            MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily_positive:Author)
            WHERE bob <> lily_positive
                AND neighbor.test=TRUE
                AND bob.test = TRUE
                AND lily_positive.test = TRUE
                AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily_positive))
                AND EXISTS((bob)-[:COLLABORATE_TEST]-(lily_positive))
            WITH  bob, lily_positive, COUNT(DISTINCT neighbor) AS common_neighbor_count, 1 AS existed
            WITH bob, 
                COLLECT(lily_positive) AS collect_postive, 
                COLLECT(existed) AS collect_existed,
                COLLECT(common_neighbor_count) AS collect_score_postive

            MATCH (bob)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily_negative:Author)
            WHERE bob <> lily_negative
                AND neighbor.test=TRUE
                AND bob.test = TRUE
                AND lily_negative.test = TRUE
                AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily_negative))
                AND NOT EXISTS((bob)-[:COLLABORATE_TEST]-(lily_negative))
            WITH  bob, 
                collect_postive,
                collect_score_postive,
                collect_existed,
                lily_negative, 
                COUNT(DISTINCT neighbor) AS common_neighbor_count,
                -1 AS not_existed
            WITH bob, 
                collect_postive,
                collect_score_postive,
                collect_existed,
                COLLECT(lily_negative) AS collect_negative, 
                COLLECT(common_neighbor_count) AS collect_score_negative,
                COLLECT(not_existed) AS collect_not_existed
            WITH bob, 
                collect_postive,
                SIZE(collect_postive) AS num_positive,
                SIZE(collect_negative) AS num_negative,
                collect_score_postive,
                collect_existed,
                collect_negative, 
                collect_score_negative,
                collect_not_existed
            WITH bob, 
                collect_postive,
                CASE num_positive > num_negative WHEN TRUE THEN num_negative ELSE num_positive END AS num_row_by_bob,
                collect_score_postive,
                collect_existed,
                collect_negative, 
                collect_score_negative,
                collect_not_existed
            WITH bob, 
                collect_postive,
                RANGE(0,num_row_by_bob-1,1) AS coll_size,
                collect_score_postive,
                collect_existed,
                collect_negative, 
                collect_score_negative,
                collect_not_existed
            UNWIND coll_size AS idx
            WITH bob, 
                collect_postive[idx] AS positive, 
                collect_score_postive[idx] AS score_postive,
                collect_existed[idx] AS existed,
                collect_negative[idx] AS negative, 
                collect_score_negative[idx] AS score_negative,
                collect_not_existed[idx] AS not_existed
            WITH bob, 
                COLLECT (positive) AS collect_postive, 
                COLLECT (score_postive) AS collect_score_postive,
                COLLECT (existed) AS collect_existed,
                COLLECT (negative) AS collect_negative, 
                COLLECT (score_negative) AS collect_score_negative,
                COLLECT (not_existed) AS collect_not_existed
            WITH bob, 
                collect_postive + collect_negative AS collect_friend, 
                collect_score_postive + collect_score_negative AS collect_friend_score,
                collect_existed + collect_not_existed AS collect_existed
            WITH bob, 
                collect_friend, 
                collect_friend_score,
                collect_existed,
                SIZE(collect_friend) AS num_row
            WITH bob, 
                collect_friend, 
                collect_friend_score,
                collect_existed,
                RANGE(0,num_row-1,1) AS row_num_list
            UNWIND row_num_list AS idx
            WITH bob, 
                collect_friend[idx] AS friend, 
                collect_friend_score[idx] AS score,
                collect_existed[idx] AS existed
            
            ORDER BY existed DESC, score DESC, bob.author_id DESC
            RETURN bob.author_id AS joined_date_bob, 
                friend.author_id AS joined_date_friend, 
                score,  
                existed
            """
    result = graph.run(query)
    # query = """
    #         MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND ]->(lily:Author)
    #         WHERE bob.test=TRUE AND lily.test=TRUE AND bob<>lily
    #         WITH DISTINCT r.score AS score,
    #             bob.author_id AS bob_joined_date,
    #             lily.author_id AS lily_joined_date,
    #             r.top AS top,
    #             CASE EXISTS((bob)-[:COLLABORATE_TEST ]-(lily)) WHEN TRUE THEN 1 ELSE -1 END AS is_existed

    #         ORDER BY is_existed DESC, score
    #         RETURN score,
    #             bob_joined_date,
    #             lily_joined_date,
    #             top,
    #             is_existed
    #         """
    # result = graph.run(query)
    toList = list(result)
    N = len(toList)
    dimension = len(toList[0]) - 1
    training_pairs = [[0.0 for d in range(0, dimension + 1)]
                      for n in range(0, N)]
    for n, row in enumerate(toList):
        for idx in range(0, dimension + 1):
            training_pairs[n][idx] = row[idx]
    # print("dimension", dimension, training_pairs[0])
    return training_pairs


def train_svm(graph, ):
    training_pairs = prepare_data_svm(graph)
    print("training_pairs", training_pairs)
    draw_data(training_pairs)
    # from algorithm.svm import run

    # dimension = len(training_pairs[0]) - 1
    # # print("dimension", dimension, "traing_pairs", traing_pairs)
    # (w, b) = run(training_pairs, d=dimension)
    # from utils.file import write_csv

    # write_csv("common_neighbor_svm.csv", [[w, b]],
    #           header="w|b",
    #           toStr=lambda row: '[{0}]|{1}'.format(
    #               ",".join(str(w_n) for w_n in row[0]),
    #               row[1])
    #           )


def load_svm_model() -> list:
    from utils.file import load_model
    import ast
    model = load_model("common_neighbor_svm.csv",
                       toList=lambda reader: [
                           ast.literal_eval(reader[1][0]),
                           float(reader[1][1])
                       ])
    return model


def recommend(x):
    model = load_svm_model()
    if (len(model < 1)):
        raise 'Exception: No model has been found!!'

    w = list(model[0])
    _x = list(x)
    b = model[1]
    y = w.dot(_x) + b > 0
    if (y):
        return True
    return False


# def valuate(graph):
#     query = """
#             CALL {
#                 MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]->(lily:Author)
#                 WHERE bob <> lily
#                     AND bob.test = TRUE
#                     AND lily.test = TRUE
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                 WITH DISTINCT r.top AS top, bob, lily, 0 AS fp_element
#                 RETURN DISTINCT top, COUNT(fp_element) AS fp, 0 AS tp
#                 UNION
#                 MATCH (bob:Author)-[r:COMMON_NEIGHBOR_RECOMMEND]->(lily:Author)
#                 WHERE bob <> lily
#                     AND bob.test = TRUE
#                     AND lily.test = TRUE
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                     AND EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                 WITH DISTINCT r.top AS top, bob, lily, 1 AS tp_element
#                 RETURN DISTINCT top, COUNT(tp_element) AS tp, 0 AS fp
#             }
#             WITH top, SUM(tp) AS tp, SUM(fp) AS fp
#             WITH top, tp, tp+fp AS tp_fp
#             WITH DISTINCT top, tp * 1.0/ tp_fp AS precision

#             ORDER BY top DESC
#             RETURN top, precision
#             """

#     precision = []
#     for idx, row in enumerate(graph.run(query)):
#         # print("done")
#         print("{0}-{1}".format(row[0], row[1]))
#         # print("{0}-{1}: {2}".format(row[0], row[1], row[2]))

#     # 5-0.022066198595787363
#     # 4-0.026078234704112337
#     # 3-0.03009027081243731
#     # 2-0.0320962888665998
#     # 1-0.037111334002006016

#     return precision
