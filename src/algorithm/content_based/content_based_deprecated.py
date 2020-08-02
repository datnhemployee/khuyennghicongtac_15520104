from models.algorithm import Algorithm
from utils.db import db

from models.step import Step

from datetime import datetime

from stop_words import get_stop_words
from collections import defaultdict

from threading import Thread, Lock
import heapq
import csv

from math import sqrt

_temp_content_based = "public/contentBased.csv"
_temp_file = _temp_content_based


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
        print("ContentBased-start",  datetime.now())
        project_uid = int(kw.get("project_uid"))
        cb_end = kw.get("cb_end", None)
        from utils.file import deleteFileIfExisted
        deleteFileIfExisted(_temp_file)

        from services.neo4j_service import neo4jService
        num_author = neo4jService.get_num_author(project_uid, "prior")
        # num_author = 10000
        print("done-get_num_author", num_author)

        self.delete_predictions(project_uid)
        topK = 10

        documents = ["" for author_idx in range(num_author)]
        authors = [-1 for author_idx in range(num_author)]
        # recommendation_list = [[(-1, -1, -1) for top in range(topK)]
        #                        for author_idx in range(num_author)]

        query = """
            MATCH (bob:Author)-[:UPLOAD]->(w:Work)
            WHERE bob.prior_{uid}=TRUE AND
                w.prior_{uid}=TRUE
            WITH bob, COLLECT(DISTINCT w.title) AS publish_collection
            RETURN bob.author_id AS author_id,
                REDUCE(initAray='', title IN publish_collection|initAray + title ) AS publish_activity_description""".format(
            uid=project_uid,)

        for (idx, row) in enumerate(db.run(query,)):
            authors[idx] = row[0]
            documents[idx] = row[1]

        # print("done-get_profile")

        temp_doc = stopWord(documents)
        temp_doc = removeUncommonWord(temp_doc)
        documents = None

        lock = Lock()
        print("start-build_lstBow_dctWordIdx_AuthorIdx",)

        (lstBow, lstBow_scalar,
         dct_wordIdx_author) = build_lstBow_dctWordIdx_AuthorIdx(temp_doc)
        print("end-build_lstBow_dctWordIdx_AuthorIdx",)
        print("end-lstBow",)
        for (idx, bow) in enumerate(lstBow):
            print(idx, bow, )
        print("end-lstBow_scalar",)
        for bow in lstBow_scalar:
            print(bow)
        print("end-dct_wordIdx_author",)
        for key in dct_wordIdx_author.keys():
            print(key, dct_wordIdx_author[key])

        gap = 1000
        num_threads = round(num_author / gap)

        lstThreads = [ContentBasedThread(
            lock=lock,
            authors=authors,
            lstBow=lstBow,
            lstBow_scalar=lstBow_scalar,
            dct_wordIdx_author=dct_wordIdx_author,
            startIndex=idx_thread * gap,
            idx=idx_thread,
            gap=get_real_gap(
                num_author, idx_thread * gap, gap),
            topK=10)
            for idx_thread in range(num_threads + 1)]

        for (idx, adaThread) in enumerate(lstThreads):
            adaThread.start()

        for adaThread in lstThreads:
            adaThread.join()
        print("done all threads",)

        if (cb_end is not None):
            cb_end()
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
