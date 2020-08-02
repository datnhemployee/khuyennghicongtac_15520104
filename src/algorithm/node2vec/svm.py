def get_node2vec(emb_file="src/algorithm/emb"):
    from gensim.models import KeyedVectors
    model = KeyedVectors.load_word2vec_format(emb_file)
    return model


def get_dimension(emb_file="src/algorithm/emb"):
    with open(emb_file) as f:
        first_line = f.readline()
        temp = first_line.split(" ")
        f.close()
        return int(temp[1])


def prepare_training_pair_link_label(graph, operator="average") -> list:
    '''
    Get all collaborations from Neo4j network to map to networkx.
    '''
    query = """
        CALL {
                MATCH (bob:Author)-[:COLLABORATE_TEST]-(lily:Author)
                WHERE bob <> lily
                    AND bob.test =true
                    AND lily.test =true
                    AND NOT EXISTS((bob)-[:COLLABORATE_PRIOR]-(lily))
                RETURN DISTINCT  bob, lily, 1 AS existed
                UNION
				MATCH (bob:Author)-[:COLLABORATE_PRIOR]-(lily:Author)
                WHERE bob <> lily
                    AND bob.test =true
                    AND lily.test =true
                    AND NOT EXISTS((bob)-[:COLLABORATE_TEST]-(lily))
                RETURN DISTINCT  bob, lily, -1 AS existed
            }
            WITH DISTINCT bob.author_id AS bob,
				lily.author_id AS lily,
				existed

			ORDER BY existed DESC,lily
			WITH existed,
				COLLECT(bob) AS bob,
				COLLECT(lily) AS lily
			WITH existed,
				bob,
				lily,
				SIZE(bob) AS bob_size,
				SIZE(lily) AS lily_size
			WITH existed,
				bob,
				lily,
				CASE bob_size>lily_size WHEN TRUE THEN lily_size ELSE bob_size END AS size
			WITH existed,
				bob,
				lily,
				RANGE(0,size -1,1) AS row_idx
			UNWIND row_idx AS idx
			RETURN bob[idx] AS bob, lily[idx] AS lily, existed
    """
    result = graph.run(query)
    result = list(result)

    dimension = get_dimension()
    vector_label = [[0.0 for d in range(dimension + 1)] for l in result]
    model = get_node2vec()
    # print("vocab", model)
    if(operator == "average"):
        for idx, row in enumerate(result):
            start_node = model[str(row[0])]
            end_node = model[str(row[1])]
            print("row", row[2])
            vector = (start_node + end_node) * 0.5
            vector_label[idx][-1] = row[2]
            for d, val in enumerate(vector):
                vector_label[idx][d] = val

        return vector_label
