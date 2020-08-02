
def run(graph, neighbourhood_size=5):

    query = """
          MATCH (:Author)-[r:JACCARD_COEFFICIENT]-(:Author)
          DELETE r
          """
    graph.run(query)
    query = """
          MATCH (:Author)-[r:JACCARD_COEFFICIENT_RECOMMEND]-(:Author)
          DELETE r
          """
    graph.run(query)
    query = """
          MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
          WHERE bob <> lily
              AND bob.prior =TRUE
              AND lily.prior =TRUE
              AND neighbor.prior=TRUE
              AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
          WITH  bob, 
            lily, 
            COUNT(DISTINCT neighbor) AS intersection_count,
            SIZE((bob)-[:COLLABORATE_PRIOR]-(:Author)) AS num_neighBob,
            SIZE((lily)-[:COLLABORATE_PRIOR]-(:Author)) AS num_neighLily
            
          WITH bob, lily, intersection_count, (num_neighBob+ num_neighLily) - intersection_count AS union_count

          WITH bob, lily, (intersection_count*1.0/union_count) as jaccard_index

          // Get top k neighbours based on Common Neighbor
          ORDER BY  jaccard_index DESC, lily.author_id
          WITH bob,
              COLLECT(lily)[0..$k] AS recommendations,
              COLLECT(jaccard_index)[0..$k] AS common_neighbor_count_list,
              RANGE(0,$k-1,1) AS coll_size
          UNWIND coll_size as idx
          WITH bob, recommendations[idx] as friend, idx AS top
          WHERE NOT friend IS NULL
          CREATE (bob)-[:JACCARD_COEFFICIENT { top:top } ]->(friend)
          """
    recos = {}
    graph.run(query, parameters={'k': neighbourhood_size})
    # for idx, row in enumerate(graph.run(query)):
    #     # print("{0}-{1}: {2}/{3}".format(row[0], row[1], row[2], row[3]))
    #     print("{0}-{1}: {2}".format(row[0], row[1], row[2]))
    #     # print("{0}-{1}".format(row[0], row[1]))
    print("JACCARD_COEFFICIENT: Done")

    # start:2020-06-18 07:50:01.543735
    # JACCARD_COEFFICIENT_RECOMMEND: Done
    # end:2020-06-18 07:50:07.473788
    # seconds:5.930053

    return recos


# def valuate(graph):
#     query = """
#             CALL {
#                 MATCH (bob:Author)-[r:JACCARD_COEFFICIENT_RECOMMEND]->(lily:Author)
#                 WHERE bob <> lily
#                     AND bob.test = TRUE
#                     AND lily.test = TRUE
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                 WITH DISTINCT r.top AS top, bob, lily, 0 AS fp_element
#                 RETURN DISTINCT top, COUNT(fp_element) AS fp, 0 AS tp
#                 UNION
#                 MATCH (bob:Author)-[r:JACCARD_COEFFICIENT_RECOMMEND]->(lily:Author)
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

#     return precision
