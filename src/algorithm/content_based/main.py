import numpy as np
from collections import defaultdict
from gensim import corpora
from stop_words import get_stop_words
from math import sqrt
import random


def stopWord(text_corpus):
    stopList = get_stop_words('english')
    texts = [[word for word in document.lower().split() if word not in stopList]
             for document in text_corpus]
    return texts


def removeUncommonWord(text_corpus):
    frequency = defaultdict(int)
    for line in text_corpus:
        for token in line:
            frequency[token] += 1
    texts = [
        [token for token in text if frequency[token] > 1]
        for text in text_corpus
    ]
    return texts


def cosine(vector1: list, vector2: list) -> float:
    numerator = 0
    if (len(vector1) == 0 or len(vector2) == 0):
        return 0.0
    denominator = 0.0
    for e1 in vector1:
        key1 = e1[0]
        val1 = e1[1]

        _e2 = [e2 for e2 in vector2 if e2[0] == key1]
        existed = len(_e2) != 0
        if (existed):
            e2 = _e2[0]
            val2 = e2[1]
            numerator += val1*val2

        denominator1 = sum([(e[1]*e[1]) for e in vector1])
        denominator2 = sum([(e[1]*e[1]) for e in vector2])
        denominator = sqrt(denominator1 * denominator2)

        if (denominator == 0.0):
            print("Lỗi chia 0")
            raise "Error: divine by zero - Cosine similar"

    return numerator * 1.0 / denominator


def getTopK(bow_corpus: list, authors: list, neighbourhood_size=5):
    # Return Similar matrix
    # ------ [i] ------>
    #             au1 |au[i]| au3 | ...
    #  |    au1    X  |  copy  |  copy  |  copy
    #  |    ___________________________
    #       au[k]  ?  |  X  |  copy  |  copy
    # [k]   ___________________________
    #       au3    ?  |  ?  |  X  |  copy
    #  |    ___________________________
    #  V    ...    ?  |  ?  |  ?  |  X
    # the value "?" shall be computed
    # the value "X" shall be skipped
    dimension = len(authors)
    dictListAuthor = np.array([[[float(authors[author_index_column]), 0.0] for author_index_column in range(dimension)]
                               for author_index_row in range(dimension)])

    for tuple_k in enumerate(dictListAuthor):
        k = tuple_k[0]
        i = 0
        while (i < k):

            profile_vector_k = bow_corpus[k]

            # calculate similarity between vector of auk and au[0..(k-1)]
            profile_vector_pre_k = bow_corpus[i]
            similarity = 0.0
            try:
                similarity = cosine(profile_vector_k, profile_vector_pre_k)
            except:
                i += 1
                continue

            dictListAuthor[k][i][1] = similarity
            dictListAuthor[i][k][1] = similarity
            i += 1

    result = dictListAuthor.tolist()

    for author_profile in result:
        author_profile.sort(
            key=lambda cell_similar_authorIndex_value: cell_similar_authorIndex_value[1], reverse=True)

    temp = np.array(result)
    result = (temp[:, :neighbourhood_size]).tolist()

    result = [[authors[index], author_similarity[0], author_similarity[1]]
              for (index, sublist) in enumerate(result) for author_similarity in sublist]
    return result


def deleteFileIfExisted(filename):
    import os
    import errno
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def write_csv(output_filename: str,  list_content: list):
    try:
        deleteFileIfExisted(output_filename)
        with open(output_filename, mode='w', encoding='UTF-8') as output_file_writer:
            output_file_writer.write(':START_ID|:END_ID|similarity:float\n')
            for listItem in list_content:
                output_file_writer.write('{0}|{1}|{2}\n'.format(
                    listItem[0], listItem[1], listItem[2]))
    except Exception as e:
        print("err:", e)


def toDB(graph, list_content_based_recommendation: list, neighbourhood_size=5):
    query = """
            MATCH (:Author)-[r:CONTENT_BASED]-(:Author)
            DELETE r
          """
    graph.run(query)
    query = """
            MATCH (:Author)-[r:CONTENT_BASED_RECOMMEND]-(:Author)
            DELETE r
          """
    graph.run(query)
    query = """
        MATCH (bob:Author),(lily:Author)
        WHERE bob.author_id = $start AND
            lily.author_id = $end AND
            NOT EXISTS((bob)-[:CONTENT_BASED]->(lily))
        CREATE (bob)-[:CONTENT_BASED {
            score: $score
        }]->(lily)
        """

    for content_based_recommendation in list_content_based_recommendation:

        start = content_based_recommendation[0]
        end = content_based_recommendation[1]
        score = content_based_recommendation[2]
        graph.run(query, parameters={
                  'start': start, 'end': end, 'score': score})

    query = """
            MATCH (bob:Author)-[r:CONTENT_BASED]->(lily:Author)
            WHERE bob <> lily
                AND bob.prior = TRUE
                AND lily.prior = TRUE
                AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
            WITH DISTINCT r, bob, lily

            ORDER BY r.score, bob
            WITH DISTINCT bob, 
                COLLECT(lily) AS  bob_friends, 
                COLLECT(r) AS bob_recommendations
            WITH DISTINCT bob, 
                bob_friends, 
                bob_recommendations,
                SIZE(bob_friends) AS num_recommendations
            WITH DISTINCT bob, 
                bob_friends, 
                bob_recommendations,
                RANGE(0,num_recommendations -1,1) AS list_idx
            UNWIND list_idx AS idx
            WITH DISTINCT bob, 
                bob_friends[idx] AS friend, 
                bob_recommendations[idx] AS recommendation,
                idx AS top
            MATCH (bob)-[recommendation]->(friend)
            SET recommendation.top =top
            """
    graph.run(query)


def run(graph, neighbourhood_size=5):
    print("CONTENT_BASED: Start")

    query = """
        MATCH (bob:Author)-[:UPLOAD]-(w:Work)
        WHERE bob.prior=TRUE AND 
            EXISTS(w.title) AND 
            w.year >= 2010 AND 
            w.year <= 2015 AND 
            w.prior=TRUE
        WITH bob, COLLECT(DISTINCT w.title) AS publish_collection
        RETURN bob.author_id AS author_id, 
            REDUCE(initAray='', title IN publish_collection|initAray + title ) AS publish_activity_description
        """
    text_corpus = []
    authors = []
    for idx, row in enumerate(graph.run(query)):
        text_corpus.append(row[1])
        authors.append(row[0])

    processed_corpus = stopWord(text_corpus)
    processed_corpus = removeUncommonWord(processed_corpus)

    dictionary = corpora.Dictionary(processed_corpus)
    bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]
    recommendation_topK = getTopK(bow_corpus, authors, neighbourhood_size=5)
    # write_csv("recomendation_content_based_top_10.csv", recommendation_top10)
    toDB(graph, recommendation_topK, neighbourhood_size)

    print("CONTENT_BASED: End")
    return recommendation_topK


# def valuate(graph):

#     query = """
#             CALL {
#                 MATCH (bob:Author)-[r:CONTENT_BASED]->(lily:Author)
#                 WHERE bob <> lily
#                     AND bob.test = TRUE
#                     AND lily.test = TRUE
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                 WITH DISTINCT r.top AS top, bob, lily, 0 AS fp_element
#                 RETURN DISTINCT top, COUNT(fp_element) AS fp, 0 AS tp
#                 UNION
#                 MATCH (bob:Author)-[r:CONTENT_BASED]->(lily:Author)
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

#     # 4-0.0
#     # 3-0.0
#     # 2-0.0
#     # 1-0.004219409282700422
#     # 0-0.010852713178294573

#     return precision


# def svm_run(graph):

#     query = """
#         MATCH (bob:Author)-[r:CONTENT_BASED_RECOMMEND ]-(:Author)
#         WHERE bob.test=TRUE
#         WITH DISTINCT bob.author_id AS author_id,
#             r.score AS x,
#             CASE EXISTS((bob:Author)-[:COLLABORATE_TEST]-(:Author)) WHEN TRUE THEN 1 ELSE -1 END AS y
#         RETURN author_id, x, y
#         """

#     result = graph.run(query)
#     toList = list(result)
#     N = len(toList)
#     X = np.array([[0.0 for x_idx in range(N)]])
#     V = np.array([[0.0 for v_idx in range(N)]])
#     y = np.array([[0.0 for y_idx in range(N)]])
#     # X =
#     for idx, row in enumerate(toList):
#         X[0][idx] = row[1]
#         V[0][idx] = row[1] * row[2]
#         y[0][idx] = row[2]

#     print("X", X)
#     return (X, V, y, N)
