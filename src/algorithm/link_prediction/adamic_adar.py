
def run(graph, neighbourhood_size=5):
    query = """
          MATCH (:Author)-[r:ADAMIC_ADAR]-(:Author)
          DELETE r
          """
    graph.run(query)
    query = """
          MATCH (:Author)-[r:ADAMIC_ADAR_RECOMMEND]-(:Author)
          DELETE r
          """
    graph.run(query)

    query = """
          MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(neighbor:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
          WHERE bob <> lily
              AND neighbor.prior =true
              AND bob.prior =true
              AND lily.prior =true
              AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
          WITH  bob, lily, neighbor, SIZE((neighbor)-[:COLLABORATE_PRIOR]-(:Author)) AS neighbor_neigh
          WITH  bob, lily, neighbor, 1.0/LOG(neighbor_neigh) AS inner_index
          WITH  bob, lily, SUM(inner_index) AS adamic_adar_index

          // Get top k neighbours based on Common Neighbor
          ORDER BY  adamic_adar_index DESC, lily.author_id
          WITH bob,
              COLLECT(lily)[0..$k] AS recommendations,
              COLLECT(adamic_adar_index)[0..$k] AS common_neighbor_count_list,
              RANGE(0,$k-1,1) AS coll_size
          UNWIND coll_size as idx
          WITH bob, recommendations[idx] as friend, idx AS top
          WHERE NOT friend IS NULL
          CREATE (bob)-[:ADAMIC_ADAR { top:top }]->(friend)
          """
    recos = {}
    graph.run(query, parameters={'k': neighbourhood_size})
    # for idx, row in enumerate(graph.run(query)):
    #     # print("{0}-{1}: {2}/{3}".format(row[0], row[1], row[2], row[3]))
    #     print("{0}-{1}: {2}".format(row[0], row[1], row[2]))
    #     # print("{0}-{1}".format(row[0], row[1]))
    print("ADAMIC_ADAR: Done")

    # start:2020-06-18 07:56:03.178546
    # ADAMIC_ADAR_RECOMMEND: Done
    # end:2020-06-18 07:56:10.114065
    # seconds:6.935519

    return recos


# def valuate(graph):
#     query = """
#             CALL {
#                 MATCH (bob:Author)-[r:ADAMIC_ADAR_RECOMMEND]->(lily:Author)
#                 WHERE bob <> lily
#                     AND bob.test = TRUE
#                     AND lily.test = TRUE
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                     AND NOT EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                 WITH DISTINCT r.top AS top, bob, lily, 0 AS fp_element
#                 RETURN DISTINCT top, COUNT(fp_element) AS fp, 0 AS tp
#                 UNION
#                 MATCH (bob:Author)-[r:ADAMIC_ADAR_RECOMMEND]->(lily:Author)
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
