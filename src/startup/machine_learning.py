

def create_machine_learning_database(
        graph
):

    num_positive = 0
    """
      Hủy tất cả mẫu dương
    """
    query = """
      MATCH (:Author)-[r:Y_POS]-(:Author)
      DELETE r
    """
    """
      Hủy tất cả mẫu âm
    """
    query = """
      MATCH (:Author)-[r:Y_NEG]-(:Author)
      DELETE r
    """
    graph.run(query, parameters={"num_y": num_positive})
    """
    lấy tất cả mẫu dương là liên kết đồng tác giả xuất hiện [2016-2020]
    """
    query = """
      MATCH (:Author)-[r:COLLABORATE_TEST]->(:Author)
      RETURN COUNT(DISTINCT r) AS num_y
    """
    for idx, row in enumerate(graph.run(query)):
        num_positive = row[0]

    query = """
      MATCH (a:Author)-[:COLLABORATE_TEST]->(b:Author)
      WITH DISTINCT a, b LIMIT $num_y
      WHERE NOT EXISTS((a)-[:Y_POS]-(b)) 
      CREATE (a)-[:Y_POS]->(b)
    """
    graph.run(query, parameters={"num_y": num_positive})

    """
    Tạo số mẫu âm là liên kết đồng tác giả không xuất hiện [2016-2020]
    """
    query = """
      MATCH (a:Author), (b:Author)
      WHERE a<>b AND 
        a.prior=TRUE AND
        b.prior=TRUE AND
        NOT EXISTS((a)-[:COLLABORATE_TEST]-(b)) 
      WITH DISTINCT a, b LIMIT $num_y
      WHERE NOT EXISTS((a)-[:Y_NEG]-(b)) 
      CREATE (a)-[:Y_NEG]->(b)
    """
    graph.run(query, parameters={"num_y": num_positive})

    """
    Chọn 50% mẫu dương cho học máy
    """
    half = int(num_positive/2)
    query = """
      MATCH (:Author)-[r:Y_POS]->(:Author)
      WITH DISTINCT r LIMIT $num_y
      SET r.learn=TRUE
    """
    graph.run(query, parameters={"num_y": half})

    """
    Chọn 50% mẫu âm cho học máy
    """
    query = """
      MATCH (:Author)-[r:Y_NEG]->(:Author)
      WITH DISTINCT r LIMIT $num_y
      SET r.learn=TRUE
    """
    graph.run(query, parameters={"num_y": half})
