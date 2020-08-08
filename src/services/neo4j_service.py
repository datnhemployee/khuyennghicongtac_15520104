
from utils.file import connect_path_file, PATH_PUBLIC_FOLDER, existing_file, PATH_AUTHORS_DATABASE, PATH_PRIOR_GRAPH_DATABASE, PATH_TEST_GRAPH_DATABASE
from models.project import Project
from models.author import Author
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

    def isConnect(self):
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
                "There is no connection. Check connection and try again !")

        return True

    def get_author(self, author_id: int, project_uid: int, model_id: int, similarity=None, source_id=None) -> Author:
        query = """
            MATCH (a:Author)
            WHERE a.prior_{uid}=TRUE AND
                a.author_id= $aId
            RETURN a.author_id,
                a.name""".format(
                uid=project_uid,
                _id=model_id
        )

        parameters = {
            "aId": int(author_id),
        }

        if (source_id is not None):
            query += ", EXISTS((a)-[:prior_{uid}]-(:Author ".format(
                uid=project_uid)
            query += "{ author_id: $source_id })) AS acquaintance"
            query += ", EXISTS((a)-[:test_{uid}]-(:Author ".format(
                uid=project_uid)
            query += "{ author_id: $source_id })) AS real_connected"

            parameters["source_id"] = int(source_id)

        result = {
            "author_id": None,
            "name": None,
            "similarity": None,
            "acquaintance": None,
            "real_connected": None
        }

        for row in db.run(query, parameters=parameters):
            result["author_id"] = int(row[0])
            result["name"] = row[1]
            result["similarity"] = similarity
            if (source_id is not None):
                result["acquaintance"] = row[2]
                result["real_connected"] = row[3]

        if (result["name"] is None):
            return None

        result = Author(
            result["author_id"],
            result["name"],
            result["similarity"],
            result["acquaintance"],
            result["real_connected"],
        )
        return result

    def get_authors(self, project_uid: int, model_id: int, num_authors: int) -> list:
        query = """
            MATCH (a:Author)
            WHERE a.prior_{uid}=TRUE
            RETURN DISTINCT a.author_id,
                a.name LIMIT $num_authors
            """.format(
                uid=project_uid,
                _id=model_id
        )
        result = [None for idx_author in range(num_authors)]
        for (idx, row) in enumerate(db.run(query, parameters={"num_authors": int(num_authors)})):
            result[idx] = Author(
                int(row[0]),
                row[1],
            )

        result = [author for author in result if author is not None]
        if (len(result) == 0):
            return None
        return result

    def delete_all_authors(self):
        try:
            query = """
                MATCH (a:Author)
                DETACH DELETE a
                """
            print("query", query)
            db.run(query,)
        except:
            raise ValueError(
                "There is no connection found. Check connection and try again !")

    def _init_new_prior_collaborations(self, uid):
        try:
            query = """
                    USING PERIODIC COMMIT 1000
                    LOAD CSV WITH HEADERS FROM $path AS line FIELDTERMINATOR ','
                    WITH line.`a` AS a_author_id,
                        line.`b` AS b_author_id 

                    MATCH (a:Author)
                    MATCH (b:Author)
                    WHERE a.author_id=toInteger(a_author_id) AND
                        b.author_id=toInteger(b_author_id)
                    """
            query += """
                CREATE (a)-[:prior_{uid}]->(b)""".format(uid=uid)
            db.run(query, parameters={"path": PATH_PRIOR_GRAPH_DATABASE})
            print("query", query)
        except Exception as e:
            print("err", e.args)
            raise ValueError(
                "There is no connection found. Check connection and try again !")

    def _init_new_test_collaborations(self, uid):
        try:
            query = """
                    USING PERIODIC COMMIT 1000
                    LOAD CSV WITH HEADERS FROM $path AS line FIELDTERMINATOR ','
                    WITH line.`a` AS a_author_id,
                        line.`b` AS b_author_id 

                    MATCH (a:Author)
                    MATCH (b:Author)
                    WHERE a.author_id=toInteger(a_author_id) AND
                        b.author_id=toInteger(b_author_id)
                    """
            query += """
                CREATE (a)-[:test_{uid}]->(b)""".format(uid=uid)
            print("query", query)
            db.run(query, parameters={"path": PATH_TEST_GRAPH_DATABASE})
        except:
            raise ValueError(
                "There is no connection found. Check connection and try again !")

    def _init_new_prior_authors(self, uid):
        try:
            parameters = "{ "
            parameters += " author_id:toInteger(author_id), name:name, neigh_{uid}:num_col, work_prior_{uid}:num_work, prior_{uid}:TRUE".format(
                uid=uid,)
            parameters += " })"
            query = """
                    USING PERIODIC COMMIT 1000
                    LOAD CSV WITH HEADERS FROM $path AS line FIELDTERMINATOR ','
                    WITH line.`author_id` AS author_id,
                        line.`name` AS name,
                        line.`num_work` AS num_work,
                        line.`num_col` AS num_col

                    CREATE (:Author {parameters} """.format(parameters=parameters)
            print("query", query)
            db.run(query, parameters={"path": PATH_AUTHORS_DATABASE})
        except:
            raise ValueError(
                "There is no connection found. Check connection and try again !")

    def initNew(self, uid, _id):
        self.delete_all_authors()
        self._init_new_prior_authors(uid)
        self._init_new_prior_collaborations(uid)
        self._init_new_test_collaborations(uid)


neo4jService = Neo4jService()
