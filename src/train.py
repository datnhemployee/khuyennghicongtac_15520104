from utils.db import db

project_uid = 1


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
            "Error: No author is found in database.")
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
            "Error: No paper is found in database.")
    return True


def init():
    from utils.file import AUTHOR_PAPER_DATABASE, PAPER_DATABASE

    try:
        existsAuthor = isExistAuthor()
        existsPaper = isExistAuthor()

        if (existsAuthor == False or existsPaper == False):
            deleteAll()
        else:
            print("done")
            return

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

        query = """
            USING PERIODIC COMMIT 1000
            LOAD CSV WITH HEADERS FROM $path AS line FIELDTERMINATOR '|'
            WITH line.`article:ID` AS work_id,
            line.`year:int` AS year,
            line.`title:string` AS title

            MATCH (w:Work { work_id: toInteger(work_id) })
            SET w.year = toInteger(year), w.title = title """

        db.run(query, parameters={"path": PAPER_DATABASE})

        from utils.file import AUTHOR_DATABASE
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
    except ValueError as e:
        print(e.args)
    print("done")


def get_node2vec():
    from models.node2vec import Node2vec
    from models.project import Project
    project = Project()

    algorithm = Node2vec(

        p=1.0,
        q=1.0,

        num_walks=10,
        walk_length=80,

        dimensions=128,
        window_size=5,
    )
    return algorithm


def get_content_based():
    from models.content_based import ContentBased
    algorithm = ContentBased()
    return algorithm


def get_common_neighbor():
    from models.common_neighbor import CommonNeighbor
    algorithm = CommonNeighbor()
    return algorithm


def get_adamic_adar():
    from models.adamic import Adamic
    algorithm = Adamic()
    return algorithm


def get_jaccard_coefficient():
    from models.jaccard import Jaccard
    algorithm = Jaccard()
    return algorithm


def train_and_valuate(algorithm):
    if (algorithm is None):
        print("No algorithm has been found to train.")
        return
    print("start-train-{0}".format(algorithm.name))
    algorithm.train(project_uid=project_uid)
    print("start-valuate-{0}".format(algorithm.name))
    algorithm.valuate(project_uid=project_uid)
    print("done")


def train():
    """
    init new database
    """
    init()
    model = None
    """
    train_and_valuate: Node2vec
    """
    model = get_node2vec()

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
