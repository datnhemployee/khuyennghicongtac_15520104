
def valuate(graph, recommendation_type=None, predicate=None):
    if (recommendation_type == None):
        raise "Error: No recommendation type was found!"
    true_positive = 0
    false_positive = 1
    false_negative = 0

    precision = 0
    recall = 0
    f_measure = 0

    _predicate = ""
    if (predicate is not None):
        _predicate = predicate
    query = """
            MATCH (a:Author)-[r:{0}]->(lily:Author)
            WHERE lily.prior = TRUE
                AND EXISTS((a)-[:COLLABORATE_TEST]-(lily))
                {1}
            RETURN COUNT(r) AS tp
            """.format(recommendation_type, _predicate)

    for idx, row in enumerate(graph.run(query,)):
        true_positive = row[0]

    # fp: Số liên kết không đúng nhưng vẫn được tiên đoán
    # lấy số liên kết cần tiên đoán tại mỗi nút
    # xem trong topk' với k'<5 và k'=số liên kết cần tiên đoán tại mỗi nút,
    # có bao nhiêu tiên đoán sai
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

    # fn: Số liên kết thật sự đúng nhưng không được tiên đoán
    # 1.Tìm số liên kết cần tiên đoán tại mỗi nút num_col,  num_col <= 5
    # 2.Số liên kết thật sự đúng và được chưa tiên đoán trong giới hạn num_col =
    #   num_col - Số liên kết thật sự đúng và được tiên đoán trong giới hạn num_col
    query = """
            MATCH (a:Author)-[r:COLLABORATE_TEST]-(b:Author)
            WITH DISTINCT a, COUNT(DISTINCT b.author_id) AS num_col
            
            MATCH (a)-[r:{0}]->(lily:Author)
            WHERE lily.prior = TRUE
                AND r.top < num_col
            WITH a, CASE EXISTS((a)-[:COLLABORATE_TEST]-(lily)) WHEN TRUE THEN 1 ELSE 0 END AS existed, num_col
            WITH a, SUM(existed) AS true_positive, COLLECT(num_col) AS num_col
            WITH a, num_col[0]- true_positive AS false_negative
            RETURN SUM(false_negative) AS false_negative
            """.format(recommendation_type)
    for idx, row in enumerate(graph.run(query,)):
        false_negative = row[0]

    precision = true_positive * 1.0/(true_positive + false_positive)
    recall = true_positive * 1.0/(true_positive + false_negative)
    f_measure = 2*precision * recall * 1.0/(precision + recall)
    print("precision", precision, "recall", recall, "f_measure", f_measure)
    return (precision, recall, f_measure)
