# Implements user-user collaborative filtering using the following steps:
#   1. For each user, select top k similar user who rate the same as user
#   3. Identify products purchased by the top k neighbours that have not been purchased by the target user
#   4. Rank these products by the number of purchasing neighbours
#   5. Return the top n recommendations for each user
import numpy as np


def memory_based_run(graph, neighbourhood_size, similarity_func="cosine"):
    print("memory_based_run: Start")
    # print("memory_based_run: {0}".format(neighbourhood_size))
    query = """
            MATCH (:Author)-[r:COLLABORATIVE_FILTERING]-(:Author)
            WHERE r.type_sim = $type_sim
            DELETE r
          """
    graph.run(query, parameters={'type_sim': similarity_func})

    similarity_calculation = """
            // Get cosine_index = numerator/SQRT(denominator1*denominator2)
            MATCH (bob:Author)-[bob_neighbor:RATE_PRIOR]->(neighbor:Author)<-[lily_neighbor:RATE_PRIOR]-(lily:Author)
            WHERE bob <> lily AND
                bob.prior=TRUE AND
                lily.prior=TRUE AND
                neighbor.prior=TRUE 
            WITH bob,
                lily,
                SUM(bob_neighbor.rating*lily_neighbor.rating) AS numerator

            MATCH (bob)-[bob_rate:RATE_PRIOR]->()
            WITH bob,
                lily,
                numerator,
                SUM(bob_rate.rating*bob_rate.rating) AS denominator1

            MATCH (lily)-[lily_rate:RATE_PRIOR]->()
            WITH bob,
                lily,
                numerator,
                denominator1,
                SUM(lily_rate.rating*lily_rate.rating) AS denominator2

            WITH bob,
                lily,
                numerator* 1.0/SQRT(denominator1*denominator2) AS similarity
            """

    if (similarity_func == "pearson"):
        similarity_calculation = """
            MATCH (bob:Author)-[bob_neighbor:RATE_PRIOR]->(neighbor:Author)<-[lily_neighbor:RATE_PRIOR]-(lily:Author)
            WHERE bob.prior=TRUE AND
                lily.prior=TRUE AND
                neighbor.prior=TRUE AND
                bob <> lily
            WITH bob,
                lily,
                bob_neighbor.rating AS bob_neighbor_rating,
                lily_neighbor.rating AS lily_neighbor_rating

            MATCH (bob)-[bob_rate:RATE_PRIOR]->(:Author)
            WITH bob,
                lily,
                bob_neighbor_rating,
                lily_neighbor_rating,
                SUM(bob_rate.rating) AS numerator_mean_bob_rating

            MATCH (lily)-[lily_rate:RATE_PRIOR]->(:Author)
            WITH bob,
                lily,
                bob_neighbor_rating,
                lily_neighbor_rating,
                numerator_mean_bob_rating,
                SUM(lily_rate.rating) AS numerator_mean_lily_rating

            WITH bob,
                lily,
                numerator_mean_bob_rating* 1.0/ SIZE((bob)-[:RATE_PRIOR]->(:Author)) AS mean_bob_rating,
                numerator_mean_lily_rating* 1.0/ SIZE((lily)-[:RATE_PRIOR]->(:Author)) AS mean_lily_rating,
                bob_neighbor_rating,
                lily_neighbor_rating

            WITH bob,
                lily,
                (bob_neighbor_rating - mean_bob_rating) AS A,
                (lily_neighbor_rating - mean_lily_rating) AS B

            WITH bob,
                lily,
                A*B AS nominator,
                A*A AS denominator1,
                B*B AS denominator2

            WITH bob,
                lily,
                SUM(nominator) AS nominator,
                SUM(denominator1) AS denominator1,
                SUM(denominator2) AS denominator2

            WITH bob,
                lily,
                nominator,
                SQRT(denominator1*denominator2) AS denominator

            WHERE denominator <> 0.0

            WITH bob,
                lily,
                nominator* 1.0/denominator AS similarity
        """

    query = similarity_calculation + """
            // Get top k neighbours based on similarity
            ORDER BY similarity DESC, lily.author_id
            WITH bob,
                COLLECT(lily)[0..$k] as neighbours,
                COLLECT(similarity)[0..$k] as similarity_list,
                RANGE(0,$k - 1,1) AS coll_size
            UNWIND coll_size as idx
            WITH bob, neighbours[idx] as neighbour, similarity_list[idx] as similarity
            WHERE NOT neighbour IS NULL
            WITH bob, neighbour, similarity

            MATCH (bob)-[:RATE_PRIOR]->(:Author)<-[:RATE_PRIOR]-(neighbour)-[r_neighbor_friend:RATE_PRIOR]->(friend_neighbor:Author)
            WHERE neighbour.prior=TRUE AND
                friend_neighbor.prior=TRUE AND
                bob <> friend_neighbor AND
                neighbour <> friend_neighbor AND
                NOT EXISTS ((bob)-[:RATE_PRIOR]->(friend_neighbor))
            WITH bob, 
                friend_neighbor, 
                SUM(r_neighbor_friend.rating) AS bob_rating_friend_neighbor,
                COUNT(r_neighbor_friend) AS num_rating
            WITH bob, friend_neighbor, bob_rating_friend_neighbor/num_rating AS rating
            WITH bob, friend_neighbor, CASE rating WHEN 0 THEN 1 ELSE rating END AS new_rating

            ORDER BY rating DESC, friend_neighbor.author_id
            WITH bob,
                COLLECT(friend_neighbor)[0..$k] AS friends,
                COLLECT(new_rating)[0..$k] AS rating_list,
                RANGE(0,$k - 1,1) AS coll_size
            UNWIND coll_size AS idx
            WITH bob,
                friends[idx] AS friend_recommend,
                rating_list[idx] AS rating_relevant,
                idx AS top
            WHERE NOT friend_recommend IS NULL
            WITH bob,
                friend_recommend,
                rating_relevant,
                top
            CREATE (bob)-[:COLLABORATIVE_FILTERING { rating: rating_relevant,
                type_sim: $type_sim,
                top:top }]->(friend_recommend)
        """
    # print("query: {0}".format(query))

    graph.run(query, parameters={
        'k': neighbourhood_size,
        'type_sim': similarity_func})
    print("memory_based_run: End")


def model_based_run(graph, neighbourhood_size, model="kmeans"):
    print("model_based_run: Start")
    print("model_based_run: {0}".format(neighbourhood_size))

    refresh = """
        MATCH (clustered_node:Author)
        WHERE EXISTS(clustered_node.cluster)
        REMOVE clustered_node.cluster, clustered_node.center
    """
    graph.run(refresh)
    refresh = """
        MATCH (:Author)-[r:COLLABORATIVE_FILTERING ]-(:Author)
        WHERE EXISTS(r.model) 
        DELETE r
    """
    graph.run(refresh)
    refresh = """
        MATCH (:Author)-[r:COLLABORATIVE_FILTERING_RECOMMEND ]-(:Author)
        WHERE EXISTS(r.model) 
        DELETE r
    """
    graph.run(refresh)

    # clustering with k-means
    model_algorithm = """
        MATCH (test_node:Author)
        WHERE test_node.prior = true
        WITH test_node,
            SIZE((test_node)-[:COLLABORATE_PRIOR]-(:Author)) AS num_collaboration
        ORDER BY num_collaboration DESC, test_node.author_id
        WITH test_node LIMIT 100
        SET test_node.centre=TRUE
        WITH COLLECT(test_node) AS center_list

        MATCH (bob:Author)
        WHERE bob.prior = true AND NOT bob IN center_list
        WITH bob, center_list

        UNWIND center_list AS centre
        WITH bob, centre

        MATCH (bob)-[rating_bob:RATE_PRIOR]->(:Author)<-[rating_center:RATE_PRIOR]-(centre)
        WHERE bob <> centre
        WITH bob, centre, rating_bob.rating - rating_center.rating AS rating_difference
        WITH bob, centre, rating_difference*rating_difference AS pow2_rating_difference
        WITH bob, centre, SUM(pow2_rating_difference) AS pow2_rating_difference

        ORDER BY pow2_rating_difference ASC, centre.author_id
        WITH bob,
            COLLECT(centre)[0..1] AS top_nearest_centre,
            COLLECT(pow2_rating_difference)[0..1] AS pow2_rating_difference_list
        WITH bob,
            top_nearest_centre[0] AS center,
            pow2_rating_difference_list[0] AS distance
        WITH DISTINCT center, bob
        SET center.cluster = center.author_id,
            bob.cluster=center.author_id
    """
    graph.run(model_algorithm)

    """
    Method: Euclidean distance [k-means paper]
    """
    collaborative_filtering = """
        MATCH (bob:Author)-[bob_rating:RATE_PRIOR]->(mid:Author)<-[lily_rating:RATE_PRIOR]-(lily:Author)-[r:RATE_PRIOR]->(other:Author)
        WHERE lily.prior = true AND
            bob.prior=true AND
            other.prior=TRUE AND
            lily.cluster=bob.cluster AND
            NOT EXISTS((bob)-[:RATE_PRIOR]->(other)) AND
            lily <> other AND
            bob <> other AND
            lily <> bob
        WITH DISTINCT bob,
            lily,
            mid,
            bob_rating.rating - lily_rating.rating AS diff_bob_lily,
            other,
            r
        WITH DISTINCT bob,
            lily,
            mid,
            diff_bob_lily*diff_bob_lily AS diff_bob_lily_pow2,
            other,
            r
        WITH DISTINCT bob,
            lily,
            SUM(diff_bob_lily_pow2) AS diff_bob_lily,
            other,
            r
        WITH DISTINCT bob,
            lily,
            SQRT(diff_bob_lily) AS diff_bob_lily,
            other,
            r
        WITH DISTINCT bob,
            lily,
            diff_bob_lily,
            other,
            r
        WITH bob,
            other,
            r.rating AS rating,
            COUNT(lily) AS times,
            diff_bob_lily

        WHERE diff_bob_lily <> 0
        WITH bob,
            other,
            rating,
            1.0/ diff_bob_lily AS diff_bob_lily,
            times
        WITH bob,
            other,
            rating,
            times * 1.0 * diff_bob_lily AS times

        ORDER BY times DESC, rating DESC
        WITH DISTINCT bob,
            other,
            COLLECT(rating) AS rating_list,
            COLLECT(times) AS times_list
        WITH bob,
            other,
            rating_list[0] AS most_time_rating,
            times_list[0] AS largest_time_number

        WITH bob,
            other,
            most_time_rating,
            largest_time_number

        ORDER BY most_time_rating DESC, other.author_id
        WITH bob,
            COLLECT(other)[0..$k] AS other_list,
            COLLECT(most_time_rating)[0..$k] AS top_rating_list,
            RANGE(0,$k-1,1) AS collect_idx
        UNWIND collect_idx AS idx
        WITH bob,
            other_list[idx] AS recommendation,
            top_rating_list[idx] AS top_rating_recommend,
            idx AS top
        WHERE NOT recommendation IS NULL AND NOT top_rating_recommend IS NULL
        CREATE (bob)-[:COLLABORATIVE_FILTERING { rating: top_rating_recommend, model: 'kmeans', top:top } ]->(recommendation)
    """

    graph.run(collaborative_filtering, parameters={'k': neighbourhood_size})
    print("model_based_run: End")

# MATCH (bob:Author)-[bob_neighbor:rate_prior]->(neighbor:Author)<-[lily_neighbor:rate_prior]-(lily:Author)
# WHERE bob <> lily AND
#   bob.hop_test=TRUE AND
#   lily.hop2_test=TRUE AND
#   neighbor.hop1_test=TRUE
# WITH bob,
#   lily,
#   SUM(bob_neighbor.rating*lily_neighbor.rating) AS numerator

# MATCH (bob)-[bob_rate:rate_prior]->()
# WITH bob,
#   lily,
#   numerator,
#   SUM(bob_rate.rating*bob_rate.rating) AS denominator1

# MATCH (lily)-[lily_rate:rate_prior]->()
# WITH bob,
#   lily,
#   numerator,
#   denominator1,
#   SUM(lily_rate.rating*lily_rate.rating) AS denominator2

# WITH bob,
#   lily,
#   numerator* 1.0/SQRT(denominator1*denominator2) AS similarity

# ORDER BY similarity DESC, lily.author_id
# WITH bob,
# COLLECT(lily)[0..10] as neighbours,
# COLLECT(similarity)[0..10] as similarity_list,
# RANGE(0,9,1) AS coll_size
# UNWIND coll_size as idx
# WITH bob, neighbours[idx] as neighbour, similarity_list[idx] as similarity
# WHERE NOT neighbour IS NULL
# WITH bob, neighbour, similarity

# MATCH (neighbour)-[hop3_rate:rate_prior]->(hop3:Author)
# WHERE hop3.hop3_test=TRUE AND
#   	bob <> hop3 AND
# 	NOT EXISTS ((bob)-[:RATE_PRIOR]->(hop3))
# WITH DISTINCT bob,
#   hop3,
#   SUM(hop3_rate.rating) AS hop3_rating,
#   COUNT(hop3_rate) AS num_rating
# WITH bob, hop3, round(hop3_rating/num_rating) AS rating
# WHERE rating <> 0
# WITH bob, hop3, rating

# ORDER BY rating ASC, hop3.author_id
# WITH bob,
# COLLECT(hop3)[0..10] AS friends,
# COLLECT(rating)[0..10] AS rating_list,
# RANGE(0,9,1) AS coll_size
# UNWIND coll_size AS idx
# WITH bob,
# friends[idx] AS friend_recommend,
# rating_list[idx] AS rating_relevant,
# idx AS top
# WHERE NOT (friend_recommend IS NULL)
# RETURN bob.author_id as bob,
# friend_recommend.author_id AS recommend,
# rating_relevant,
# top

# CALL apoc.periodic.iterate(
#   "MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author) "+
#   "WHERE a.prior_1595426051223=TRUE "+
#   "AND b.prior_1595426051223=TRUE "+
#   "AND w.prior_1595426051223=TRUE "+
#   "AND NOT EXISTS(((a)-[:rate_prior]->(b))) "+
#   "WITH DISTINCT a, "+
#   "b, "+
#   "COUNT(DISTINCT w) AS samework "+
#   "MATCH (a)-[:UPLOAD]->(w:Work) "+
#   "WHERE w.prior_1595426051223=TRUE "+
#   "WITH DISTINCT a, "+
#   "b, "+
#   "samework, "+
#   "COUNT(DISTINCT w) AS workA "+
#   "MATCH (b)-[:UPLOAD]->(w:Work) "+
#   "WHERE  w.prior_1595426051223=TRUE "+
#   "WITH DISTINCT a, "+
#   "b, "+
#   "samework, "+
#   "workA, "+
#   "COUNT(DISTINCT w) AS workB "+
#   "WITH a,b, (workB+workA-samework) AS workAB, samework "+
#   "WITH a,b, round(samework * 5.0/workAB) AS rate_a "+
#   "WHERE NOT EXISTS(((a)-[:rate_prior]->(b))) "+
#   "AND rate_a>0",
#   "CREATE (a)-[:rate_prior {rating: rate_a}]->(b)",
#   {batchMode: "BATCH",batchSize:10000, parallel:true, retries:10 })

# MATCH (a:Author)-[:UPLOAD]->(w:Work)
# WHERE a.prior_1595426051223=TRUE
# 	AND w.prior_1595426051223=TRUE
# WITH a, COUNT(DISTINCT w) AS num_w
# SET a.work_prior_1595426051223=num_w

# MATCH (a:Author)-[:UPLOAD]->(w:Work)
# WHERE a.prior_1595426051223=TRUE
# 	AND w.test_1595426051223=TRUE
# WITH a, COUNT(DISTINCT w) AS num_w
# SET a.work_prior_1595426051223=num_w

# def valuate(graph, similarity_func="cosine", model=None):
#     if (model == None):
#         query = """
#                 CALL {
#                     MATCH (bob:Author)-[r:COLLABORATIVE_FILTERING_RECOMMEND]->(lily:Author)
#                     WHERE bob <> lily
#                         AND bob.test = TRUE
#                         AND lily.test = TRUE
#                         AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                         AND NOT EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                         AND r.type_sim = $type_sim
#                     WITH DISTINCT r.top AS top, bob, lily, 0 AS fp_element
#                     RETURN DISTINCT top, COUNT(fp_element) AS fp, 0 AS tp
#                     UNION
#                     MATCH (bob:Author)-[r:COLLABORATIVE_FILTERING_RECOMMEND]->(lily:Author)
#                     WHERE bob <> lily
#                         AND bob.test = TRUE
#                         AND lily.test = TRUE
#                         AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                         AND EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                         AND r.type_sim = $type_sim
#                     WITH DISTINCT r.top AS top, bob, lily, 1 AS tp_element
#                     RETURN DISTINCT top, COUNT(tp_element) AS tp, 0 AS fp
#                 }
#                 WITH top, SUM(tp) AS tp, SUM(fp) AS fp
#                 WITH top, tp, tp+fp AS tp_fp
#                 WITH DISTINCT top, tp * 1.0/ tp_fp AS precision

#                 ORDER BY top DESC
#                 RETURN top, precision
#                 """

#         precision = []
#         for idx, row in enumerate(graph.run(query, parameters={'type_sim': similarity_func})):
#             # print("done")
#             print("{0}-{1}".format(row[0], row[1]))
#             # print("{0}-{1}: {2}".format(row[0], row[1], row[2]))

#         # cosine
#         # 4-0.01282051282051282
#         # 3-0.020497803806734993
#         # 2-0.02269861286254729
#         # 1-0.014652014652014652
#         # 0-0.020556227327690448

#         # pearson
#         # 4-0.0
#         # 3-0.0
#         # 2-0.0
#         # 1-0.0
#         # 0-0.0

#     """
#     k-means
#     """
#     query = """
#         CALL {
#             MATCH (bob:Author)-[r:COLLABORATIVE_FILTERING_RECOMMEND]->(lily:Author)
#             WHERE bob <> lily
#                 AND bob.test = TRUE
#                 AND lily.test = TRUE
#                 AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                 AND NOT EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                 AND r.model = 'kmeans'
#             WITH DISTINCT r.top AS top, bob, lily, 0 AS fp_element
#             RETURN DISTINCT top, COUNT(fp_element) AS fp, 0 AS tp
#             UNION
#             MATCH (bob:Author)-[r:COLLABORATIVE_FILTERING_RECOMMEND]->(lily:Author)
#             WHERE bob <> lily
#                 AND bob.test = TRUE
#                 AND lily.test = TRUE
#                 AND NOT EXISTS ((bob)-[:COLLABORATE_PRIOR]-(lily))
#                 AND EXISTS ((bob)-[:COLLABORATE_TEST]-(lily))
#                 AND r.model = 'kmeans'
#             WITH DISTINCT r.top AS top, bob, lily, 1 AS tp_element
#             RETURN DISTINCT top, COUNT(tp_element) AS tp, 0 AS fp
#         }
#         WITH top, SUM(tp) AS tp, SUM(fp) AS fp
#         WITH top, tp, tp+fp AS tp_fp
#         WITH DISTINCT top, tp * 1.0/ tp_fp AS precision

#         ORDER BY top DESC
#         RETURN top, precision
#         """

#     precision = []
#     for idx, row in enumerate(graph.run(query, parameters={'type_sim': similarity_func})):
#         # print("done")
#         print("{0}-{1}".format(row[0], row[1]))

#     # 4-0.015267175572519083
#     # 3-0.0
#     # 2-0.003663003663003663
#     # 1-0.007220216606498195
#     # 0-0.014184397163120567

#     return precision
