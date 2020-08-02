from models.algorithm import Algorithm
from utils.db import db

from models.step import Step


class ContentBased(Algorithm):
    def __init__(self,
                 id=None,

                 descriptions="",
                 valuations={}
                 ):
        super().__init__(name="ContentBased", id=id, setting={},
                         descriptions=descriptions,
                         valuations=valuations)
        self.recall = []

    def mapFrom(self, algorithm: Algorithm):
        self.__init__(
            id=algorithm._id,
            descriptions=algorithm.descriptions,
            valuations=algorithm.valuations,
        )

    def get_icon_path(self):
        from utils.file import ICON_CONTENT_BASED
        return ICON_CONTENT_BASED

    def train(self,
              *arg,
              **kw):
        from datetime import datetime
        project_uid = int(kw.get("project_uid"))
        print("ContentBased-start",  datetime.now())
        self.delete_predictions(project_uid)

        query = """
            MATCH (a:Author)-[:UPLOAD]->(w:Work)
            WHERE a.prior_{uid}=TRUE AND
                w.prior_{uid}=TRUE
            WITH DISTINCT a, COUNT(DISTINCT w) AS num_work
            SET a.work_prior_{uid} = num_work
        """.format(uid=project_uid)
        db.run(query)

        query = """
            MATCH (a:Author)-[:UPLOAD]->(w:Work)<-[:UPLOAD]-(b:Author)
            WHERE a.prior_{uid}=TRUE AND
                w.prior_{uid}=TRUE AND
                b.prior_{uid}=TRUE
            WITH DISTINCT a, b, COUNT(DISTINCT w) AS num_col
            WITH a, b, num_col* 1.0/(a.work_prior_{uid}*b.work_prior_{uid}) AS score
            WHERE NOT EXISTS((a)-[:cosine_{uid}]-(b))
            CREATE (a)-[:cosine_{uid} """.format(uid=project_uid)
        query = """ { score:score } ]->(b)
        """
        db.run(query)

        query = """
            MATCH (a:Author)-[r:cosine_{uid}]-(b:Author)
            WHERE a.prior_{uid}=TRUE AND
                b.prior_{uid}=TRUE
            WITH a, b, r.score AS score

            ORDER BY score DESC, b.author_id
            WITH a,
                COLLECT(b)[0..10] AS col_b,
                COLLECT(score)[0..10] AS col_score,
                RANGE(0,9,1) AS col_idx
            UNWIND col_idx AS idx
            WITH a, 
                col_b[idx] AS b, 
                col_score[idx] AS score, 
                col_idx[idx] AS top
            WHERE NOT (b IS NULL) AND
                NOT EXISTS((a)-[:_{uid}_{_id}]->(b))
            CREATE (a)-[:_{uid}_{_id} """.format(uid=project_uid, _id=self._id)
        query += """ { score:score, top:top }]->(b) """
        db.run(query)

        print("ContentBased-end", datetime.now())

    def get_step_list(self):
        step_list = [
            Step(
                name="Bước 1: Phân tích nội dung bài báo",
                inputs={
                    "Tập bài báo": "Tập bài báo",
                },
                outputs={
                    "Tập vectơ đặc trưng bài báo": "Mỗi vectơ đặc trưng là one-hot vectơ với mỗi vị trí phần tử đại diện cho thứ tự bài báo."
                },
                output_file=""),
            Step(
                name="Bước 2: Khuyến nghị theo số Common Neighbor",
                inputs={
                    "Tập vectơ đặc trưng bài báo": "Tập vectơ đặc trưng bài báo",
                    "Tập nghiên cứu viên": "Tập nghiên cứu viên",
                },
                outputs={
                    "Tập hồ sơ người dùng": "Mỗi nghiên cứu viên có vectơ là tổng các one-hot vectơ của các bài báo được công bố bởi nghiên cứu viên ấy."
                },
                output_file=""),
            Step(
                name="Bước 3: Với mỗi cặp nghiên cứu viên, tính giá trị cosine",
                inputs={
                     "Tập hồ sơ người dùng":  "Tập hồ sơ người dùng",
                },
                outputs={
                    "danh sách độ tương tự - cosine": "Danh sách các cặp nghiên cứu viên và độ tương tự giữa họ."
                },
                output_file=""),
            Step(
                name="Bước 4: khuyến nghị TopK cho mỗi nghiên cứu viên theo độ tương tự - cosine",
                inputs={
                     "danh sách độ tương tự - cosine":  "danh sách độ tương tự - cosine",
                },
                outputs={
                    "Recommendations": "Danh sách 10 nghiên cứu viên khuyến nghị cho mỗi nghiên cứu viên tương ứng."
                },
                output_file=""),
        ]
        return step_list
