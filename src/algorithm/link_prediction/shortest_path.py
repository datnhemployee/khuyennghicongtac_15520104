
def run(graph, neighbourhood_size=5):

    print("SHORTEST_PATH: Start")
    query = """
          MATCH (:Author)-[r:SHORTEST_PATH]-(:Author)
          DELETE r
          """
    graph.run(query)

    query = """
          MATCH (:Author)-[r:SHORTEST_PATH_RECOMMEND]-(:Author)
          DELETE r
          """
    graph.run(query)

    query = """
            CALL {
                MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
                WHERE bob <> lily
                    AND bob.prior =true
                    AND lily.prior =true
                    AND CASE (
                    EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
                    ) WHEN TRUE
                    THEN FALSE
                    ELSE TRUE
                    END
                RETURN  bob, lily, 2 AS length
                UNION
                MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor1:Author)-[:COLLABORATE_PRIOR]-(neighbor1:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
                WHERE bob <> lily
                    AND bob.prior =true
                    AND lily.prior =true
                    AND CASE (
                    EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
                    ) WHEN TRUE
                    THEN FALSE
                    ELSE TRUE
                    END
                RETURN  bob, lily, 3 AS length
                UNION
                MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor1:Author)-[:COLLABORATE_PRIOR]-(neighbor1:Author)-[:COLLABORATE_PRIOR]-(neighbor1:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
                WHERE bob <> lily
                    AND bob.prior =true
                    AND lily.prior =true
                    AND CASE (
                    EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
                    ) WHEN TRUE
                    THEN FALSE
                    ELSE TRUE
                    END
                RETURN  bob, lily, 4 AS length
            }
            WITH DISTINCT bob, lily, 1.0/length AS shortest_path_index

            // Get top k neighbours based on Common Neighbor
            ORDER BY shortest_path_index DESC, lily.author_id
            WITH bob,
              COLLECT(lily)[0..$k] AS recommendations,
              COLLECT(shortest_path_index)[0..$k] AS shortest_path_list,
              RANGE(0,$k-1,1) AS coll_size
            UNWIND coll_size as idx
            WITH bob, recommendations[idx] AS friend, idx AS top
            WHERE NOT friend IS NULL
            CREATE(bob)-[:SHORTEST_PATH { top:top }]->(friend)

          """
    recos = {}

    graph.run(query, parameters={'k': neighbourhood_size})

    print("SHORTEST_PATH: Done")

    # start: 2020-06-18 08: 01: 25.828733
    # SHORTEST_PATH_RECOMMEND: Start
    # SHORTEST_PATH_RECOMMEND: Done
    # end: 2020-06-18 08: 01: 30.079008
    # seconds: 4.250275

    return recos


# def valuate(graph):
#     query = """
#             CALL {
#                 MATCH (bob:Author)-[r:SHORTEST_PATH_RECOMMEND]->(lily:Author)
#                 WHERE bob <> lily
#                     AND bob.test = TRUE
#                     AND lily.test = TRUE
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                 WITH DISTINCT r.top AS top, bob, lily, 0 AS fp_element
#                 RETURN DISTINCT top, COUNT(fp_element) AS fp, 0 AS tp
#                 UNION
#                 MATCH (bob:Author)-[r:SHORTEST_PATH_RECOMMEND]->(lily:Author)
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
#     # 3-0.009027081243731194
#     # 2-0.011
#     # 1-0.011
#     # 0-0.017

#     return precision
