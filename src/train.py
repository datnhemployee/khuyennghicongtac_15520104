from utils.db import db
from utils.file import AUTHOR_PAPER_DATABASE, PAPER_DATABASE, AUTHOR_DATABASE
from controllers.main import controller

uid = controller.get_project_uid()
prior_start = 2014
prior_end = 2015

test_start = 2016
test_end = 2016


def deleteAll():
    try:
        query = """
            call apoc.periodic.iterate("MATCH (n) RETURN n LIMIT 1000;", "DETACH DELETE n", {batchSize:1000})
            yield batches, total return batches, total
        """
        db.run(query)
    except:
        raise ValueError(
            "Error: Not able to delete all.")


def isExistAuthor():
    rs = None
    query = """
        MATCH (a:Author)
        RETURN 1 AS existed LIMIT 1
    """
    try:
        for row in db.run(query,):
            rs = int(row[0])

        if (rs != 1):
            return False
    except:
        raise ValueError(
            "Error: There is an error when connecting to database.")
    return True


def isExistPaper():
    rs = None
    query = """
        MATCH (w:Work)
        RETURN 1 AS existed LIMIT 1
    """
    try:
        for row in db.run(query,):
            rs = int(row[0])

        if (rs != 1):
            return False
    except:
        raise ValueError(
            "Error: There is an error when connecting to database.")
    return True


def init_author_paper_upload():
    query = """
            // Load and commit every 1000 records
            USING PERIODIC COMMIT 1000
            LOAD CSV WITH HEADERS FROM $path AS line FIELDTERMINATOR '|'
            WITH line.`START_ID` AS work_id,
            line.`END_ID` AS author_id

            MERGE (w:Work { work_id: toInteger(work_id)})
            MERGE  (a:Author { author_id: toInteger(author_id)})

            // Create relationships between Author and Paper
            CREATE (a)-[:UPLOAD]->(w) """
    print("create new author->paper:{0}".format(query))

    db.run(query, parameters={"path": AUTHOR_PAPER_DATABASE})


def init_papers():
    query = """
        USING PERIODIC COMMIT 1000
        LOAD CSV WITH HEADERS FROM $path AS line FIELDTERMINATOR '|'
        WITH line.`article:ID` AS work_id,
        line.`year:int` AS year,
        line.`title:string` AS title

        MATCH (w:Work { work_id: toInteger(work_id) })
        SET w.year = toInteger(year), w.title = title """

    db.run(query, parameters={"path": PAPER_DATABASE})


def init_authors():
    query = """
        // Load and commit every 1000 records
        USING PERIODIC COMMIT 1000
        LOAD CSV WITH HEADERS FROM $path AS line FIELDTERMINATOR '|'
        WITH line.`ID` AS author_id,
            line.`author` AS name

        MATCH (a:Author)
        WHERE a.author_id = toInteger(author_id)
        SET a.name= name
        """
    print("create set name author:{0}".format(query))

    db.run(query, parameters={"path": AUTHOR_DATABASE})


def init():

    try:
        existsAuthor = isExistAuthor()
        existsPaper = isExistAuthor()

        if (existsAuthor == False or existsPaper == False):
            deleteAll()
        else:
            print("No need to create new DB")
            return

        init_author_paper_upload()
        init_papers()
        init_authors()

    except ValueError as e:
        print(e.args)
    print("Done - creating new DB")


def mark_prior_author(uid, ):
    query = """
        MATCH (a:Author)-[:prior_{uid}]-(:Author)
        WITH DISTINCT a
        SET a.prior_{uid}=TRUE
    """.format(uid=uid)
    db.run(query, )


def mark_test_author(uid, num_author=100):
    query = """
        MATCH (a:Author)-[:test_{uid}]-(:Author)
        WHERE a.prior_{uid}=TRUE
        WITH DISTINCT a
        SET a.test_{uid}=TRUE
    """.format(uid=uid)
    db.run(query, parameters={
        "num_author": num_author,
        "TopK": 10
    })


def mark_prior_paper(uid, start, end,):
    query = """
        MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
        WHERE a<>b AND
            a.prior_{uid} = TRUE AND
            b.prior_{uid} = TRUE AND
            EXISTS(w.title) AND
            w.year>={start} AND
            w.year<={end}
        WITH DISTINCT w
        SET w.prior_{uid}=TRUE
    """.format(uid=uid, start=start, end=end)
    db.run(query, )


def mark_test_paper(uid, start, end,):
    query = """
        MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
        WHERE a<>b AND
            a.prior_{uid} = TRUE AND
            b.prior_{uid} = TRUE AND
            EXISTS(w.title) AND
            w.year>={start} AND
            w.year<={end}
        WITH DISTINCT w
        SET w.test_{uid}=TRUE
    """.format(uid=uid, start=start, end=end)
    db.run(query, )


def update_work_prior(uid):
    query = """
        MATCH (a:Author)-[:UPLOAD]->(w:Work)
        WHERE a.prior_{uid} = TRUE AND
            w.prior_{uid}=TRUE 
        WITH a, COUNT(DISTINCT w) AS num_work
        SET a.work_prior_{uid}=num_work
    """.format(uid=uid,)
    db.run(query, )


def delete_connection(type_db):
    query = """
        MATCH (:Author)-[r:{type_db}_{uid}]-(:Author)
        DELETE r
    """.format(uid=uid, type_db=type_db)
    db.run(query,)


def create_prior_connection(uid, start, end, is_directed=False, is_weighted=False):
    if (is_directed == False and is_weighted == False):
        query = """
            MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
            WHERE a<>b AND
                EXISTS(w.title) AND
                w.year>={start} AND
                w.year<={end} AND
                NOT EXISTS((a)-[:prior_{uid}]-(b))
            CREATE (a)-[:prior_{uid}]->(b)
        """.format(uid=uid, start=start, end=end)
        db.run(query,)

    elif (is_directed == False and is_weighted == True):
        query = """
            MATCH (a:Author)-[:prior_{uid}]->(b:Author)
            WHERE a.prior_{uid}=TRUE AND
                b.prior_{uid}=TRUE
            WITH a, b

            MATCH (a)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b) 
            WHERE w.prior_{uid}=TRUE
            WITH DISTINCT a,b,
                COUNT(w) AS same_work
            WITH  a, 
                 b,
                same_work* 1.0/(a.work_prior_{uid} + b.work_prior_{uid} - same_work) AS score
            WHERE NOT EXISTS((a)-[:prior_weight_{uid}]->(b))
            CREATE (a)-[:prior_weight_{uid}""".format(uid=uid,)
        query += """{ score:score } ]->(b)"""
        db.run(query,)

    elif (is_directed == True and is_weighted == True):
        query = """
            MATCH (a:Author)-[:prior_{uid}]-(b:Author)
            WHERE a.prior_{uid}=TRUE AND
                b.prior_{uid}=TRUE
            WITH a,b

            MATCH (a)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b) 
            WHERE w.prior_{uid}=TRUE
            WITH DISTINCT  a, 
                b,
                COUNT(w) AS same_work
            WITH DISTINCT  a, 
                b,
                same_work* 1.0/(a.work_prior_{uid}) AS score
            CREATE (a)-[:prior_dir_weight_{uid}""".format(uid=uid, start=start, end=end)
        query += """{ score:score } ]->(b)"""
        db.run(query,)


def create_test_connection(uid, start, end,):
    query = """
        MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
        WHERE a<>b AND
            a.prior_{uid}=TRUE AND
            b.prior_{uid}=TRUE AND
            EXISTS(w.title) AND
            w.year>={start} AND
            w.year<={end} AND
            NOT EXISTS((a)-[:test_{uid}]-(b))
        CREATE (a)-[:test_{uid}]->(b)
    """.format(uid=uid, start=start, end=end)
    db.run(query,)


def init_prior(uid, start, end,):
    create_prior_connection(uid, start, end,)
    mark_prior_author(uid, )
    mark_prior_paper(uid, start, end,)
    "set {work_prior} for every authors"
    update_work_prior(uid)
    "create (weight, no direction) connection"
    create_prior_connection(
        uid, start, end, is_directed=False, is_weighted=True)
    "create (weighted, directed) connection"
    create_prior_connection(
        uid, start, end, is_directed=True, is_weighted=True)


def init_test(uid, start, end,):
    create_test_connection(uid, start, end,)
    mark_test_author(uid, )
    mark_test_paper(uid, start, end,)


def get_node2vec():
    from models.node2vec import Node2vec
    from models.project import Project
    project = Project()
    """
    model: emb1596901817640
    start-time:2020-08-08 22:50:17.647283
    start-valuate-Node2vec 2020-08-09 00:26:36.885709
    true_positive 177065 false_positive 966205 false_negative 390357
    precision 0.15487592607170658 recall 0.31205170049804204 f_measure 0.20700979486663876
    num_node  319247
    """
    # algorithm = Node2vec(

    #     p=1.5,
    #     q=0.5,

    #     num_walks=10,
    #     walk_length=80,

    #     dimensions=128,
    #     window_size=5,
    # )

    """
    model: emb1596908253117
    start-time:2020-08-09 00:37:33.178716
    start-valuate-Node2vec 2020-08-09 02:10:50.464838
    true_positive 176269 false_positive 967001 false_negative 391153
    precision 0.15417967759147008 recall 0.3106488645135367 f_measure 0.2060791773153788
    num_node  319247
    """

    # algorithm = Node2vec(

    #     p=0.5,
    #     q=1.5,

    #     num_walks=10,
    #     walk_length=80,

    #     dimensions=128,
    #     window_size=5,
    # )

    """
    model: emb1596938427561
    start-time:2020-08-09 09:00:27.560990
    start-valuate-Node2vec 2020-08-09 10:39:00.384716
    true_positive 180248 false_positive 963022 false_negative 387174
    precision 0.15766004530863226 recall 0.317661282079299 f_measure 0.21073109595415188
    num_node  319247

    is_directed=True
    is_weighted=True
    """
    # algorithm = Node2vec(

    #     p=1,
    #     q=1,

    #     num_walks=10,
    #     walk_length=80,

    #     is_directed=True,
    #     is_weighted=True,

    #     dimensions=128,
    #     window_size=5,
    # )

    """
    model: emb1596945404872
    start-time:2020-08-09 10:56:44.872109
    start-valuate-Node2vec 2020-08-09 12:35:31.081626
    true_positive 181092 false_positive 962178 false_negative 386330
    precision 0.15839827862184785 recall 0.31914871118849814 f_measure 0.21171783114669385
    num_node  319247

    is_directed=True
    is_weighted=True
    """
    # # algorithm = Node2vec(

    # #     p=1.5,
    # #     q=0.5,

    # #     num_walks=10,
    # #     walk_length=80,

    # #     is_directed=True,
    # #     is_weighted=True,

    # #     dimensions=128,
    # #     window_size=5,
    # # )

    """
    model: emb1596978210771
    start-time:2020-08-09 20:03:30.770640
    start-valuate-Node2vec 2020-08-09 22:56:59.711070
    true_positive 193930 false_positive 949340 false_negative 373492
    precision 0.16962747207571266 recall 0.3417738473305582 f_measure 0.22672696195457745
    done 2020-08-09 22:58:52.677243
    num_node  319247
    """
    # algorithm = Node2vec(

    #     p=1.5,
    #     q=0.5,

    #     num_walks=10,
    #     walk_length=80,

    #     is_directed=False,
    #     is_weighted=True,
    #     iterations=2,

    #     dimensions=128,
    #     window_size=20,
    # )

    # start-time: 2020-08-09 23: 18: 36.197567
    # true_positive 200628 false_positive 942642 false_negative 366794
    # precision 0.17548610564433598 recall 0.35357811293887087 f_measure 0.2345577111484709
    # validate-name:  Node2vec
    # precision 0.18
    # recall 0.35
    # fmeasure 0.23
    # done 2020-08-10 04: 09: 06.568617
    # algorithm = Node2vec(

    #     p=3,
    #     q=0.3,

    #     num_walks=10,
    #     walk_length=80,

    #     is_directed=True,
    #     is_weighted=True,
    #     iterations=4,

    #     dimensions=128,
    #     window_size=20,
    # )
    algorithm = Node2vec(

        p=3,
        q=0.3,

        num_walks=10,
        walk_length=80,

        is_directed=True,
        is_weighted=True,
        iterations=4,

        dimensions=128,
        window_size=20,
    )

    return algorithm


def get_content_based():
    from models.content_based import ContentBased
    """
    ContentBased-start 2020-08-10 16:48:03.550902
    ContentBased-end 2020-08-10 16:51:47.440084
    start-valuate-ContentBased 2020-08-10 16:51:47.440084
    true_positive 202309 false_positive 448784 false_negative 365113
    precision 0.3107221241819525 recall 0.35654063465991803 f_measure 0.33205828405887494
    """
    algorithm = ContentBased()
    return algorithm


def get_common_neighbor():
    from models.common_neighbor import CommonNeighbor
    """
    start:2020-08-10 16:13:41.612405
    start- commonNeighbor 1595426051223
    start-valuate-CommonNeighbor 2020-08-10 16:39:11.640779
    true_positive 184220 false_positive 807561 false_negative 383202
    precision 0.1857466517305736 recall 0.32466136314771016 f_measure 0.2363002123520799
    """
    algorithm = CommonNeighbor()
    return algorithm


def get_adamic_adar():
    from models.adamic import Adamic
    """
    start:2020-08-10 13:31:38.237319
    start- AdamicAdar 1595426051223 1597041098236
    delete preiction: Done- AdamicAdar 1595426051223 1597041098236
    start-valuate-AdamicAdar 2020-08-10 14:27:47.133518
    true_positive 196989 false_positive 794792 false_negative 370433
    precision 0.1986214698607858 recall 0.3471648966730229 f_measure 0.25267909310077
    """
    algorithm = Adamic()
    return algorithm


def get_jaccard_coefficient():
    from models.jaccard import Jaccard
    """
    start:2020-08-10 12:58:37.590622
    start- JaccardCoefficient 1595426051223
    start-valuate-Jaccard 2020-08-10 13:25:59.583218
    true_positive 166524 false_positive 825257 false_negative 400898
    precision 0.16790400300066244 recall 0.2934746978439327 f_measure 0.21360143611832452
    """
    algorithm = Jaccard()
    return algorithm


def train_and_valuate(algorithm):
    if (algorithm is None):
        print("No model has been found to train.")
        return

    print("start-train-{0}".format(algorithm.name))
    from datetime import datetime
    print("start-time:{0}".format(datetime.now()))
    algorithm.train(project_uid=uid)
    print("start-valuate-{0}".format(algorithm.name), datetime.now())
    result = algorithm.valuate(project_uid=uid)
    print("validate-name: ", algorithm.name,)
    for key in result.keys():
        print(key, result[key])
    print("done", datetime.now())


def train():
    """
    init new database
    """

    init()

    is_create_prior_db = False
    if (is_create_prior_db == True):
        delete_connection("prior")
        init_prior(uid, prior_start, prior_end)

    is_create_test_db = False
    if (is_create_test_db == True):
        delete_connection("test")
        init_test(uid, test_start, test_end)

    model = None
    """
    train_and_valuate: Node2vec
    """
    # model = get_node2vec()

    """
    train_and_valuate: Content based
    """
    # model = get_content_based()

    """
    train_and_valuate: Common Neighbors
    """
    # model = get_common_neighbor()
    """
    train_and_valuate: Adamic Adar
    """
    # model = get_adamic_adar()

    """
    train_and_valuate: Jaccard Coefficient
    """
    # model = get_jaccard_coefficient()

    train_and_valuate(model)


train()
