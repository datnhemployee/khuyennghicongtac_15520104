"""
Các loại liên kết trong mạng đồng tác giả

+ Tập huấn luyện:
  1. COLLABORATE_PRIOR: cộng tác
  1. RATE_PRIOR: đánh giá

+ Tập đánh giá:
  1. COLLABORATE_TEST: cộng tác
  1. RATE_TEST: đánh giá
"""
RELATIONSHIP_TYPE = {
    "COLLABORATE_TEST": "test",
    "COLLABORATE_PRIOR": "prior",
    "RATE_TEST": "test",
    "RATE_PRIOR": "prior",
}


def _delete_relationships(graph=None, name=None, start_node_name=None, end_node_name=None):
    """
    Hủy liên kết trong mạng đồng tác giả

    Parameters:
      + `name`: tên các loại liên kết
      + `start_node_name`: loại nút đầu
      + `end_node_name` (Optional): loại nút đích
    """

    if (name not in RELATIONSHIP_TYPE.keys() or start_node_name == None):
        return False

    _end_node_name = start_node_name
    if (end_node_name is not None):
        _end_node_name = end_node_name

    _relationship_type = "({1})-[{0}]-({2})".format(name,
                                                    start_node_name, _end_node_name)
    print("Status: Deleting all relationships {0} from Main database \n".format(
        _relationship_type))
    query = """
      MATCH (:{1})-[r:{0}]-(:{2})
      DELETE r
      """.format(name, start_node_name, _end_node_name)
    graph.run(query)
    print(
        "Status: Deleting all relationships {0} from Main database successfully \n".format(_relationship_type))
    return True


def _delete_node_label(graph=None, label=None, database_type="prior"):
    """
      Hủy bài báo nhãn test=TRUE trong mạng đồng tác giả

      Parameters:
      + `label`: Work - công trình nghiên cứu/ Author: nghiên cứu viên
      + `database_type`: prior - tập huấn luyện/ test: tập đánh giá
    """

    print("Status: Removing all ({0}:{1}) from database\n".format(
        label, database_type))
    query = """
      MATCH (w:{0})
      WHERE w.{1}=TRUE
      REMOVE w.{1}
      """.format(label, database_type)
    graph.run(query)
    print("Status: All ({0}:{1}) have been removed successfully \n".format(
        label, database_type))


def _get_created_author(graph, database_type="prior"):
    collaboration_type = "COLLABORATE_PRIOR"
    if (database_type != "prior"):
        collaboration_type = "COLLABORATE_TEST"
    result = 0
    query = """
      MATCH (a:Author)-[:{0}]-(:Author)
      RETURN COUNT(DISTINCT a) AS num_a
    """.format(collaboration_type)
    for idx, row in enumerate(graph.run(query)):
        result = row[0]

    return result


def _get_created_work(graph, database_type="prior", min_year=2010, max_year=2015):
    """
      Kiểm tra số bài báo trong mạng

      Parameters:
      + `database_type`: Loại mạng tương ứng `prior`-mạng huấn luyện/ `test`-mạng đánh giá.
      + `min_year`: năm bắt đầu xét.
      + `max_year`: năm kết thúc xét.
    """
    collaboration_type = "COLLABORATE_PRIOR"
    if (database_type != "prior"):
        collaboration_type = "COLLABORATE_TEST"

    result = 0
    query = """
        MATCH (w:Work)
        WHERE w.{0}=TRUE AND w.year>={1} AND w.year<={2}
        RETURN COUNT(DISTINCT w) AS num_paper
      """.format(collaboration_type, min_year, max_year)
    for idx, row in enumerate(graph.run(query)):
        result = row[0]

    return result


def _init_connected_prior_CoNet(graph, num_author=1000, min_year=2010, max_year=2015):
    """
      Khởi tạo mạng đồng tác giả liên kết:
        + tập huấn luyện:
          + 1000 nghiên cứu viên từng đăng báo khoa học 2010-2015.
          + Mỗi nghiên cứu viên có ít nhất 1 tác giá giả cộng tác
          + Đồ thị liên thông

      Parameters:
      + `num_author`: Số lượng tác giả ước lượng sẽ tồn tại 1 công trình có max_connected đồng tác giả.
      + `min_year`: năm bắt đầu xét.
      + `max_year`: năm kết thúc xét.

    """
    print("Status: _init_connected_prior_CoNet:\n",
          "\t+ Number of authors: {0} \n".format(num_author),
          "\t+ Min published year: {0} \n".format(min_year),
          "\t+ Max published year: {0} \n".format(max_year),
          )

    query = """
      MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
      WHERE EXISTS(w.title) AND
        w.year>={0} AND
        w.year<={1}
      WITH a, b, w LIMIT 1
      SET a.prior=TRUE AND
        b.prior=TRUE AND
        w.prior=TRUE
    """.format(
        min_year,
        max_year,
    )
    graph.run(query)

    query = """
      MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
      WHERE EXISTS(w.title) AND
        w.year>={0} AND
        w.year<={1}
      WITH a, b, w LIMIT 1
      CREATE (a)-[:COLLABORATE_PRIOR]->(b)
    """.format(
        min_year,
        max_year
    )
    graph.run(query)

    print("Status: _init_connected_prior_CoNet: Successfully")


def _expand_connected_prior_CoNet(graph, limitation=1000, min_year=2010, max_year=2015):
    """
      Mở rộng mạng đồng tác giả liên thông đã khởi tạo từ trước.

      Parameters:
      + `limitation`: Số lượng tác giả còn cần phải tạo.
      + `min_year`: năm bắt đầu xét.
      + `max_year`: năm kết thúc xét.

    """
    query = """
            MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
            WHERE EXISTS(w.title) AND
              w.year>={0} AND
              w.year<={1} AND
              EXISTS((b)-[:COLLABORATE_PRIOR]-(:Author)) AND
              NOT EXISTS((a)-[:COLLABORATE_PRIOR]-(:Author))
            WITH DISTINCT a, b LIMIT $limitation
            WHERE NOT EXISTS((a)-[:COLLABORATE_PRIOR]-(b))
            CREATE (a)-[:COLLABORATE_PRIOR]->(b)
            """.format(min_year, max_year)
    graph.run(query, parameters={'limitation': limitation})


def _init_connected_test_CoNet(graph, num_author=1000, min_year=2016, max_year=2020, max_connected=3):
    """
      Khởi tạo mạng đồng tác giả liên kết.

      Parameters:
      + `num_author`: Số lượng tác giả ước lượng sẽ tồn tại 1 công trình có max_connected đồng tác giả.
      + `min_year`: năm bắt đầu xét.
      + `max_year`: năm kết thúc xét.
      + `max_connected`: mỗi nghiên cứu viên phải cộng tác với ít nhất max_connected nên cần tạo mạng con
      chứa max_connected nghiên cứu viên.

      * Khả năng tạo là 3 - nếu không sẽ bị lỗi `Java heap - không đủ tài nguyên tính toán`
    """

    print("Status: _init_connected_test_CoNet:\n",
          "\t+ Number of authors: {0} \n".format(num_author),
          "\t+ Min published year: {0} \n".format(min_year),
          "\t+ Max published year: {0} \n".format(max_year),
          "\t+ Max connected: {0} \n".format(max_connected),
          )

    query = """
      MATCH (w1:Work)<-[:UPLOAD]-(a:Author)
      WHERE EXISTS(w1.title) AND
        w1.year>={0} AND
        w1.year<={1}
      WITH w1, a LIMIT {2}
      WITH w1, a
      ORDER BY a.author_id DESC
      WITH w1,
        COLLECT(DISTINCT a)[0..10] AS coll_a
      WHERE SIZE(coll_a)>={3}
      WITH w1, coll_a
      ORDER BY SIZE(coll_a) DESC
      WITH w1, coll_a LIMIT 1
      UNWIND coll_a AS a
      WITH w1, a
      SET w1.test=TRUE,
        a.test=TRUE
    """.format(
        min_year,
        max_year,
        num_author * 2,
        max_connected
    )
    graph.run(query)

    query = """
      MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
      WHERE w.test=TRUE AND
        w.year>={0} AND
        w.year<={1} AND
        NOT EXISTS((a)-[:COLLABORATE_TEST]-(b)) AND
        a <> b AND
        a.test=TRUE AND
        b.test=TRUE
      CREATE (a)-[:COLLABORATE_TEST]->(b)
    """.format(
        min_year,
        max_year
    )
    graph.run(query)

    print("Status: _init_connected_test_CoNet: Successfully")


# def _expand_connected_test_CoNet(graph, limitation=1000, min_year=2016, max_year=2020):
#     """
#       Mở rộng mạng đồng tác giả liên thông đã khởi tạo từ trước.

#       Parameters:
#       + `limitation`: Số lượng tác giả còn cần phải tạo.
#       + `min_year`: năm bắt đầu xét.
#       + `max_year`: năm kết thúc xét.

#       * Khả năng mỗi nghiên cứu viên liên kết là 3
#       nếu không sẽ bị lỗi `Java heap - không đủ tài nguyên tính toán`
#     """

#     print("Status: _expand_connected_test_CoNet:\n",
#           "\t+ Limitation: {0} \n".format(limitation),
#           "\t+ Min published year: {0} \n".format(min_year),
#           "\t+ Max published year: {0} \n".format(max_year),
#           )

#     query = """
#             MATCH (top1:Author)-[:UPLOAD]->(w1:Work)<-[:UPLOAD]-(a:Author)
#             MATCH (top2:Author)-[:UPLOAD]->(w2:Work)<-[:UPLOAD]-(a)
#             MATCH (top3:Author)-[:UPLOAD]->(w3:Work)<-[:UPLOAD]-(a)
#             WHERE EXISTS(w1.title) AND
#                 w1.year>={0} AND
#                 w1.year<={1} AND
#                 EXISTS(w2.title) AND
#                 w2.year>={0} AND
#                 w2.year<={1} AND
#                 EXISTS(w3.title) AND
#                 w3.year>={0} AND
#                 w3.year<={1} AND
#                 top1 <> top2 AND
#                 top3 <> top2 AND
#                 top1 <> top3 AND
#                 top1.test=TRUE AND
#                 top2.test=TRUE AND
#                 top3.test=TRUE AND
#                 NOT EXISTS(a.test)
#             WITH DISTINCT a LIMIT $limitation
#             SET a.test=TRUE
#             """.format(min_year, max_year)
#     graph.run(query, parameters={'limitation': limitation})

#     query = """
#         MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
#             WHERE EXISTS(w.title) AND
#               w.year>={0} AND
#               w.year<={1} AND
#               a <> b AND
#               b.test=TRUE AND
#               a.test=TRUE AND
#               NOT EXISTS((a)-[:COLLABORATE_TEST]-(b))
#             WITH DISTINCT a, b
#             CREATE (a)-[:COLLABORATE_TEST]->(b)
#         """.format(
#             min_year,
#             max_year,
#     )
#     graph.run(query)
#     print("Status: _expand_connected_test_CoNet: Successfully")


def _refresh_author(graph, database_type="prior"):
    """
      Thêm vào props prior/test=TRUE cho từng nút `Nghiên cứu viên`.

      Parameters:
      + `database_type`: Loại mạng tương ứng `CoNet`-mạng huấn luyện/ `CoNet'`-mạng đánh giá.

    """
    print("Status: _refresh_author:\n",
          "\t+ database_type: {0} \n".format(database_type),
          )

    collaboration_type = "COLLABORATE_PRIOR"
    if (database_type != "prior"):
        collaboration_type = "COLLABORATE_TEST"

    query = """
      MATCH (a:Author)-[:{0}]-(b:Author)
      WHERE a<>b AND (NOT EXISTS(a.{1}) OR NOT EXISTS(b.{1}))
      SET a.{1}=TRUE, b.{1}=TRUE
    """.format(
            collaboration_type,
            database_type
    )
    graph.run(query)
    print("Status: _refresh_author: Successfully")


def _refresh_work(graph, database_type="prior", min_year=2010, max_year=2015):
    """
      Thêm vào props prior/test=TRUE cho từng nút `Bài báo khoa học - Journal Article`.

      Parameters:
      + `database_type`: Loại mạng tương ứng `CoNet`-mạng huấn luyện/ `CoNet'`-mạng đánh giá.
      + `min_year`: Năm xét tối thiểu.
      + `max_year`: Năm xét tối đa.

    """
    print("Status: _refresh_work:\n",
          "\t+ database_type: {0} \n".format(database_type),
          "\t+ min_year: {0} \n".format(min_year),
          "\t+ max_year: {0} \n".format(max_year),
          )
    query = """
      MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
      WHERE EXISTS(w.title) AND
              w.year>={0} AND
              w.year<={1} AND
              b <> a AND
              b.{2}=TRUE AND
              a.{2}=TRUE
      SET w.{2}=TRUE
    """.format(
        min_year,
        max_year,
        database_type
    )
    graph.run(query)
    print("Status: _refresh_work: Successfully")


def has_dead_end_components(graph, database_type="prior"):
    """
      Kiểm tra mạng đồng tác giả có phải là đồ thị liên thông hay không

      Parameters:
      + `database_type`: Loại mạng tương ứng `CoNet`-mạng huấn luyện/ `CoNet'`-mạng đánh giá.
    """
    collaboration_type = "COLLABORATE_PRIOR"
    if (database_type != "prior"):
        collaboration_type = "COLLABORATE_TEST"

    query = """
        MATCH (root:Author)
        WHERE root.prior=TRUE
        WITH root LIMIT 1

        MATCH (a:Author)
        WHERE a.prior=TRUE AND a<>root AND NOT EXISTS((a)-[:{0}*1..1000]-(root))
        RETURN a LIMIT 1000
      """.format(collaboration_type)
    graph.run(query)
    return True


# def create_test_database(graph, num_author=1000, min_year=2016, max_year=2020):
#     # ==============================================================
#     # Choose 1000 author randomly whose has work published between 2016-2020
#     # Gieo hạt:
#     # + gieo 5 nghiên cứu viên có cùng 1 nghiên cứu trong 2016-2020
#     # + Tạo thêm
#     # + Tìm (1000 - 5) nghiên cứu viên vừa liên kết với 1 trong 5 nghiên cứu viên (bài báo 2016-2020)
#     #   và liên kết với 4 nghiên cứu viên trong số vừa gieo (bài báo 2016-2018)
#     # --> mỗi vòng lặp, if (1000 - số hạt đã gieo < 0) break
#     # database: graph
#     # Step 1:
#     # Hủy các liên kết
#     _delete_relationships(graph, name="COLLABORATE_TEST",
#                           start_node_name="Author")
#     _delete_node_label(graph, "Work", "test")
#     _delete_node_label(graph, "Author", "test")

#     # Step 2: gieo 5 nghiên cứu viên có cùng 1 nghiên cứu trong 2016-2020
#     # Khởi tạo mạng liên thông gồm 3 nghiên cứu viên liên kết cộng tác với nhau
#     _init_connected_test_CoNet(graph)

#     limitation = num_author
#     seeded = _get_created_author(graph, database_type="test")
#     limitation -= seeded

#     # Step 3: Thêm vào các nút chưa seed
#     while (limitation > 0):
#         # Mở rộng mạng liên thông gồm 3 nghiên cứu viên liên kết cộng tác với nhau
#         _expand_connected_test_CoNet(graph, limitation)
#         # lệnh tạo collaboration
#         seeded = _get_created_author(graph, database_type="test")
#         limitation = 1000-seeded
#         print("limitation={0}".format(limitation))
#     # Step 4: Thêm vào test ở các Author để dễ query
#     _refresh_author(graph, database_type="test")
#     # Step 5: Thêm vào test ở các work để dễ query
#     _refresh_work(graph, database_type="test",
#                   min_year=min_year, max_year=max_year)


# def create_disconnected_prior_CoNet_from_test_CoNet(graph, min_year=2010, max_year=2015):
#     """
#       Tạo mạng `có thể không liên thông` ở tập huấn luyện dựa vào 1000 tác giả ở tập đánh giá

#       Parameters:
#       + `min_year`: Năm xét tối thiểu.
#       + `max_year`: Năm xét tối đa.
#     """
#     query = """
#         MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
#         WHERE a<>b AND
#           a.test=TRUE AND
#           b.test=TRUE AND
#           NOT EXISTS(w.test) AND
#           EXISTS(w.title) AND
#           w.year>={0} AND
#           w.year<={1}
#         SET w.prior=TRUE
#       """.format(min_year, max_year)
#     graph.run(query)

#     query = """
#         MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
#         WHERE a<>b AND
#           a.test=TRUE AND
#           b.test=TRUE AND
#           NOT EXISTS(w.test) AND
#           EXISTS(w.title) AND
#           w.year>={0} AND
#           w.year<={1} AND
#           NOT EXISTS((a)-[:COLLABORATE_PRIOR]-(b))
#         CREATE (a)-[:COLLABORATE_PRIOR]->(b)
#       """.format(min_year, max_year)
#     graph.run(query)


def _create_disconnected_test_CoNet_from_test_CoNet(graph, min_year=2016, max_year=2020):
    """
      Tạo mạng `có thể không liên thông` ở tập huấn luyện dựa vào 1000 tác giả ở tập huấn luyện

      Parameters:
      + `min_year`: Năm xét tối thiểu.
      + `max_year`: Năm xét tối đa.
    """
    query = """
        MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
        WHERE a<>b AND
          a.prior=TRUE AND
          b.prior=TRUE AND
          NOT EXISTS(w.test) AND
          EXISTS(w.title) AND
          w.year>={0} AND
          w.year<={1}
        SET w.test=TRUE
      """.format(min_year, max_year)
    graph.run(query)

    query = """
        MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
        WHERE a<>b AND
          a.prior=TRUE AND
          b.prior=TRUE AND
          w.test=TRUE AND
          EXISTS(w.title) AND
          w.year>={0} AND
          w.year<={1} AND
          NOT EXISTS((a)-[:COLLABORATE_TEST]-(b))
        CREATE (a)-[:COLLABORATE_TEST]->(b)
      """.format(min_year, max_year)
    graph.run(query)

# def create_prior_database(graph, min_year=2010, max_year=2015):
#     """
#       Tạo mạng tập huấn luyện dựa vào 1000 tác giả ở tập đánh giá

#       Parameters:
#       + `min_year`: Năm xét tối thiểu.
#       + `max_year`: Năm xét tối đa.
#     """
#     _delete_node_label(graph, label="Work",)
#     _delete_relationships(graph, name="COLLABORATE_PRIOR",
#                           start_node_name="Author",)

#     create_disconnected_prior_CoNet_from_test_CoNet(
#         graph, min_year=min_year, max_year=max_year)


def create_test_database(graph, min_year=2016, max_year=2020):
    """
      Tạo mạng tập huấn luyện dựa vào 1000 tác giả ở tập huấn luyện

      Parameters:
      + `min_year`: Năm xét tối thiểu.
      + `max_year`: Năm xét tối đa.
    """
    _delete_node_label(graph, label="Work", database_type="test")
    _delete_relationships(graph, name="COLLABORATE_TEST",
                          start_node_name="Author",)

    _create_disconnected_test_CoNet_from_test_CoNet(graph)


def create_prior_database(graph, num_author=1000, min_year=2010, max_year=2015):
    """
      Tạo mạng đồng tác giả từ tập huấn luyện dựa vào 1000

      Parameters:
      + `min_year`: Năm xét tối thiểu.
      + `max_year`: Năm xét tối đa.
    """
    _delete_node_label(graph, label="Work",)
    _delete_node_label(graph, label="Author",)
    _delete_relationships(graph, name="COLLABORATE_PRIOR",
                          start_node_name="Author",)

    _init_connected_prior_CoNet(
        graph, min_year=min_year, max_year=max_year)

    limitation = num_author
    seeded = _get_created_author(graph)
    limitation -= seeded

    while (limitation > 0):
        # Mở rộng mạng liên thông gồm 1 nghiên cứu viên liên kết cộng tác với nhau
        _expand_connected_prior_CoNet(graph, limitation)
        # lệnh tạo collaboration
        seeded = _get_created_author(graph)
        limitation = 1000-seeded
        print("limitation={0}".format(limitation))

    _refresh_author(graph)
    _refresh_work(graph)


def import_csv_database(graph):
    """
      Thêm toàn bộ Journal Article từ DBLP vào Neo4J
    """
    try:
        graph.run("MATCH (n) DETACH DELETE n;")
        # Xóa toàn bộ constraint
        graph.run("DROP CONSTRAINT ON (w:Work) ASSERT w.work_id IS UNIQUE;")
        graph.run(
            "DROP CONSTRAINT ON(author: Author) ASSERT author.author_id IS UNIQUE;")

        # Thêm constraint
        graph.run("CREATE CONSTRAINT ON (w:Work) ASSERT w.work_id IS UNIQUE;")
        graph.run(
            "CREATE CONSTRAINT ON(author: Author) ASSERT author.author_id IS UNIQUE;")
    except:
        print("Error: Unable to create/drop constrain!")

    file_article = "file:///output_article.csv"
    file_relationship = "file:///output_author_authored_by.csv"

    query = """
        // Load and commit every 1000 records
        USING PERIODIC COMMIT 1000
        LOAD CSV WITH HEADERS FROM '{0}' AS line FIELDTERMINATOR '|'
        WITH line.`START_ID` AS work_id,
          line.`END_ID` AS author_id

        MERGE (w:Work { work_id: toInteger(work_id)})
        MERGE  (a:Author { author_id: toInteger(author_id)})

        // Create relationships between Author and Paper
        CREATE (a)-[:UPLOAD]->(w)
        """.format(file_relationship)
    graph.run(query)

    query = """
        USING PERIODIC COMMIT 500
        LOAD CSV WITH HEADERS FROM '{0}' AS line FIELDTERMINATOR '|'
        WITH line.`article:ID` AS work_id,
          line.`year:int` AS year,
          line.`title:string` AS title


        MATCH (w:Work { work_id: toInteger(work_id) })
        SET w.year = toInteger(year), w.title = title
        """.format(file_article)
    graph.run(query)


def _create_rate_prior(graph):
    """
      Thêm liên kết rate_prior cho từng cặp nghiên cứu viên
    """
    print("Status: _create_rate_relationship: PRIOR")
    _delete_relationships(graph, name="RATE_PRIOR",
                          start_node_name="Author")
    query = """
          MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
          MATCH (wa:Work)<-[:UPLOAD]-(a)
          WHERE a.prior = TRUE
            AND b.prior = TRUE
            AND a <> b
            AND w.prior = TRUE
            AND wa.prior = TRUE
            AND NOT EXISTS ((a)-[:RATE_PRIOR]->(b))
          WITH a,
            b,
            COUNT(DISTINCT w) AS intersection,
            COUNT(DISTINCT wa) AS num_work_a
          WITH a,
            b,
            intersection * 5/num_work_a AS rating
          WITH a,
            b,
            CASE rating WHEN 0 THEN 1 ELSE rating END AS normalised_rating
          CREATE (a)-[:RATE_PRIOR { rating: normalised_rating }]->(b)
        """
    graph.run(query)
    print(
        "Status: _create_rate_relationship: PRIOR - Successfully")


def _create_rate_test(graph):
    """
      Thêm liên kết rate_prior cho từng cặp nghiên cứu viên
    """
    print("Status: _create_rate_relationship: TEST")
    _delete_relationships(graph, name="RATE_TEST",
                          start_node_name="Author")
    query = """
          MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
          MATCH (wa:Work)<-[:UPLOAD]-(a)
          WHERE a.test = TRUE
            AND b.test = TRUE
            AND a <> b
            AND w.test = TRUE
            AND wa.test = TRUE
            AND NOT EXISTS ((a)-[:RATE_TEST]->(b))
          WITH a,
            b,
            COUNT(DISTINCT w) AS intersection,
            COUNT(DISTINCT wa) AS num_work_a
          WITH a,
            b,
            intersection * 5/num_work_a AS rating
          WITH a,
            b,
            CASE rating WHEN 0 THEN 1 ELSE rating END AS normalised_rating
          CREATE (a)-[:RATE_TEST { rating: normalised_rating }]->(b)
        """
    graph.run(query)
    print(
        "Status: _create_rate_relationship: TEST - Successfully")


def init(graph,
         prior={'start': 2014, 'duration': 2015},
         test={'duration': 1},
         reimport=False
         ):
    """
      Khởi tạo mạng đồng tác giả
    """
    print("RECREATE GRAPH\n",
          "+ Number of authors:", num_author,)

    if (graph == None):
        raise "Error: No graph was found!"

    if (reimport == True):
        print("Status: Importing data from csv file \n")
        import_csv_database(graph)
        print("Status: Importing data from csv file:Successfully \n")

    # print("Status: Starting creating CoNet- Test \n")
    # create_test_database(graph, num_author=num_author)
    # print("Status: Created CoNet Successfully - Test \n")

    # print("Status: Starting creating CoNet - Prior \n")
    # create_prior_database(graph)
    # print("Status: Created CoNet Successfully - Prior \n")

    print("Status: Starting creating CoNet - Prior \n")
    create_prior_database(graph)
    print("Status: Created CoNet Successfully - Prior \n")

    print("Status: Starting creating CoNet- Test \n")
    create_test_database(graph)
    print("Status: Created CoNet Successfully - Test \n")

    print("Status: Starting creating [RATE_PRIOR] \n")
    _create_rate_prior(graph)
    print("Status: Created [RATE_PRIOR] Successfully  \n")

    print("Status: Starting creating [RATE_TEST] \n")
    _create_rate_test(graph)
    print("Status: Created [RATE_TEST] Successfully \n")

    print("RECREATE GRAPH\n",
          "Status: Done \n")

    print("The CoNet test and prior graph has been initialized successfully!!!")


class AcademicCollaboratorGraph:
    def __init__(self,
                 start_year: int,
                 end_year: int,
                 mark: str):
        """
          Tham số:
          + `start_year`: Năm bắt đầu của bài báo trong mạng.
          + `end_year`  : Năm kết thúc của bài báo trong mạng.
          + `mark`: Mỗi nút (`node`) sẽ có prop `author[mark]=TRUE` hoặc `work[mark]=TRUE`.
        """
        self.start_year = start_year
        self.end_year = end_year
        self.mark = mark


class PriorAcademicCollaboratorGraph(AcademicCollaboratorGraph):
    def __init__(self, start_year=2014, end_year=2015, mark="prior"):
        """
          Tham số:
          + `start_year`: Năm bắt đầu của bài báo trong mạng (mặc định = 2014). 
          + `end_year`  : Năm kết thúc của bài báo trong mạng (mặc định = 2015).
          + `mark`: Mỗi nút (`node`) sẽ có prop `author[mark]=TRUE` hoặc `work[mark]=TRUE`. (mặc định = "prior")
        """
        super().__init__(start_year, end_year, mark)


class TestAcademicCollaboratorGraph(AcademicCollaboratorGraph):
    def __init__(self, start_year=2016, end_year=2016, mark="prior"):
        """
          Tham số:
          + `start_year`: Năm bắt đầu của bài báo trong mạng (mặc định = 2016). 
          + `end_year`  : Năm kết thúc của bài báo trong mạng (mặc định = 2016).
          + `mark`: Mỗi nút (`node`) sẽ có prop `author[mark]=TRUE` hoặc `work[mark]=TRUE`. (mặc định = "prior")
        """
        super().__init__(start_year, end_year, mark)
