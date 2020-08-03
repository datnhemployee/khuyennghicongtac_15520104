
from utils.file import connect_path_file, PATH_PUBLIC_FOLDER
from models.project import Project
from utils.db import db
import os
import io
import json


class Neo4jService():
    """
    Neo4j
    """
    """
    Prior-database
    """

    def is_init(self, uid, type_val: str):
        query = """
            MATCH (a:Author)-[:{type_val}_{uid}]-(:Author)
            RETURN a.author_id AS a LIMIT 1
        """.format(type_val=type_val, uid=uid)
        result = None
        for row in db.run(query):
            if(row is not None):
                result = row[0]
        if(result is not None):
            return True
        return False

    def mark_prior_author(self, uid, ):
        query = """
            MATCH (a:Author)-[:prior_{uid}]-(:Author)
            WITH DISTINCT a
            SET a.prior_{uid}=TRUE
        """.format(uid=uid)
        db.run(query, )

    def mark_test_author(self, uid, num_author=100):
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

    def mark_prior_paper(self, uid, start, end,):
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

    def mark_test_paper(self, uid, start, end,):
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

    def create_prior_connection(self, uid, start, end,):
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

    def create_test_connection(self, uid, start, end,):
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

    def init_prior(self, uid, start, end,):
        self.create_prior_connection(uid, start, end,)
        self.mark_prior_author(uid, )
        self.mark_prior_paper(uid, start, end,)

    def init_test(self, uid, start, end, num_author=100):
        self.create_test_connection(uid, start, end,)
        self.mark_test_author(uid, num_author)
        self.mark_test_paper(uid, start, end,)

    def get_num_author(self, uid, type_val: str) -> int:
        query = """
            MATCH (a:Author)
            WHERE a.{type_val}_{uid}=TRUE
            RETURN COUNT(DISTINCT a) AS num_author
        """.format(uid=uid, type_val=type_val)
        result = 0
        for row in (db.run(
                query,)):
            result = row[0]

        return int(result)

    def get_num_author(self, uid, type_val: str) -> int:
        query = """
            MATCH (a:Author)
            WHERE a.{type_val}_{uid}=TRUE
            RETURN COUNT(DISTINCT a) AS num_author
        """.format(uid=uid, type_val=type_val)
        result = 0
        for row in (db.run(
                query,)):
            result = row[0]

        return int(result)

    def get_num_paper(self, uid, type_val: str) -> int:
        query = """
            MATCH (w:Work)
            WHERE w.{type_val}_{uid}=TRUE
            RETURN COUNT(DISTINCT w) AS num_paper
        """.format(uid=uid, type_val=type_val)
        result = 0
        for row in (db.run(
                query,)):
            result = row[0]

        return int(result)

    def get_num_connection(self, uid, type_val) -> int:
        query = """
            MATCH (:Author)-[r:{type_val}_{uid}]-(:Author)
            RETURN COUNT(DISTINCT r) AS num_connection
        """.format(type_val=type_val, uid=uid)
        result = 0
        for row in (db.run(
            query,
        )):
            result = row[0]

        return int(result)

    def get_num_test_graph_author(self, uid) -> int:
        query = """
            MATCH (a:Author)-[:test_{uid}]-(:Author)
            RETURN COUNT(DISTINCT a) AS num_author
        """.format(uid=uid)
        result = 0
        for row in (db.run(
            query,
        )):
            result = row[0]

        return int(result)

    def get_num_prediction(self, uid,) -> int:
        query = """
            MATCH (a:Author)-[r:test_{uid}]-(:Author)
            WHERE a.test_{uid}=TRUE
            RETURN COUNT(DISTINCT r) AS num_prediction
        """.format(uid=uid)
        result = 0
        for row in (db.run(
                query,)):
            result = row[0]

        return int(result)

    def is_trained(self, project_uid: int, algorithm_id: int) -> bool:
        query = """
            MATCH (a:Author)-[r:_{project_uid}_{algorithm_id}]-(b:Author)
            WHERE a.prior_{project_uid}=TRUE AND
                b.prior_{project_uid}=TRUE AND
                a<>b
            RETURN 1 AS existed LIMIT 1
        """.format(project_uid=project_uid, algorithm_id=algorithm_id)
        result = 0
        rs = db.run(query,).data()
        for row in (rs):
            result = row['existed']
        print("algorithm_id", algorithm_id)
        if (result == 0):
            return False
        return True

    def isInited(self):
        rs = None
        query = """
            MATCH (a:Author)
            RETURN 1 AS existed LIMIT 1
        """
        try:
            for row in db.run(query,):
                rs = int(row[0])

            if (rs != 1):
                return {'status': False}

            query = """
                MATCH (w:Work)
                RETURN 1 AS existed LIMIT 1
            """
            for row in db.run(query,):
                rs = int(row[0])
        except:
            raise ValueError(
                "Không tìm thấy DBMS. Vui lòng bật Neo4j Desktop và khởi động lại chương trình.")

        if (rs != 1):
            return {'status': False}

        return {'status': True}

    def initNew(self):
        from utils.file import AUTHOR_PAPER_DATABASE, PAPER_DATABASE
        try:
            db.run("MATCH (n) DETACH DELETE n;")
            # Xóa toàn bộ constraint
        except:
            print("Error: Không thể xóa constraint")

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
        print("add detail paper:{0}".format(query))

        db.run(query, parameters={"path": PAPER_DATABASE})


neo4jService = Neo4jService()
