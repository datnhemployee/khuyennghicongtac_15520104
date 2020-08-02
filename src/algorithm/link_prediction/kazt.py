
def run(graph, neighbourhood_size=5, beta=0.85):
    query = """
          MATCH (:Author)-[r:KAZT]-(:Author)
          DELETE r
          """
    graph.run(query)
    query = """
          MATCH (:Author)-[r:KAZT_RECOMMEND]-(:Author)
          DELETE r
          """
    graph.run(query)

    print("KAZT: Start")
    query = """
        MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
        WHERE bob <> lily
            AND neighbor.prior=TRUE
            AND bob.prior =TRUE
            AND lily.prior =TRUE
            AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
        WITH DISTINCT bob,
            lily,
            (SIZE((bob)-[:COLLABORATE_PRIOR]-(:Author)-[:COLLABORATE_PRIOR]-(lily)) * $beta * $beta +
            SIZE((bob)-[:COLLABORATE_PRIOR]-(:Author)-[:COLLABORATE_PRIOR]-(:Author)-[:COLLABORATE_PRIOR]-(lily)) * $beta * $beta * $beta) AS kazt_index

        WITH bob, lily, kazt_index
        ORDER BY kazt_index DESC, lily.author_id
        WITH bob,
            COLLECT(lily)[0..$k] AS recommendations,
            COLLECT(kazt_index)[0..$k] AS katz_list,
            RANGE(0,$k-1,1) AS coll_size
        UNWIND coll_size as idx
        WITH bob, recommendations[idx] AS friend, idx AS top
        WHERE NOT friend IS NULL
        CREATE(bob)-[:KAZT { top:top }]->(friend)
        """
    recos = {}

    graph.run(query, parameters={'k': neighbourhood_size, 'beta': beta})
    print("KAZT: Done")

    # start:2020-06-18 08:23:00.228152
    # KAZT_RECOMMEND: Start
    # KAZT_RECOMMEND: Done
    # end:2020-06-18 08:23:23.882843
    # seconds:23.654691

    return recos


# def valuate(graph):
#     query = """
#             CALL {
#                 MATCH (bob:Author)-[r:KAZT_RECOMMEND]->(lily:Author)
#                 WHERE bob <> lily
#                     AND bob.test = TRUE
#                     AND lily.test = TRUE
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                 WITH DISTINCT r.top AS top, bob, lily, 0 AS fp_element
#                 RETURN DISTINCT top, COUNT(fp_element) AS fp, 0 AS tp
#                 UNION
#                 MATCH (bob:Author)-[r:KAZT_RECOMMEND]->(lily:Author)
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

#     # 4-0.020060180541624874
#     # 3-0.02106318956870612
#     # 2-0.032
#     # 1-0.019
#     # 0-0.04

#     return precision
