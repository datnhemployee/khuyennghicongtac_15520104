from models.algorithm import Algorithm
from utils.db import db

from models.step import Step

from threading import Thread, Lock
import csv
import networkx as nx
import heapq
from datetime import datetime

_temp_adamic = "public/adamic.csv"
_temp_file = _temp_adamic


def get_2_hop_u(G, u,):
    result = []
    for v in nx.neighbors(G, u):
        for neighbor in nx.neighbors(G, v):
            if (u == neighbor):
                continue
            _existed = [1 for (u, _neighbor)
                        in result if _neighbor == neighbor]
            if (len(_existed) == 0):
                result.append((u, neighbor))
    return result


def get_real_gap(num_authors: int, startIndex: int, gap: int) -> int:
    num_scan = num_authors - startIndex - gap
    if (num_scan > 0):
        return gap
    return max([num_authors - startIndex, 0])


class AdamicAdarThread(Thread):
    def __init__(self,
                 lock,
                 G,
                 lstNodes: list,
                 startIndex: int,
                 gap: int,
                 topK: int,
                 idx: int
                 ):
        Thread.__init__(self)
        self.lstNodes = lstNodes
        self.lock = lock
        self.startIndex = startIndex
        self.gap = gap
        self.G = G
        self.idx = idx
        self.topK = topK

        self.preds = [(-1, -1, -1.0) for author_idx in range(10 * self.gap)]

        print("run-", self.startIndex, self.gap,)

    def write_csv(self):
        print("start-writting", self.idx)
        from utils.file import existing_file
        self.lock.acquire()
        print("acquired-lock", self.idx)
        _is_existed = existing_file(_temp_file)
        if (_is_existed == False):
            with open(_temp_file, "w") as _file:
                wr = csv.writer(_file, quoting=csv.QUOTE_NONE,
                                delimiter="|",)
                wr.writerows(self.preds)
        else:
            with open(_temp_file, "a") as _file:
                wr = csv.writer(_file, quoting=csv.QUOTE_NONE,
                                delimiter="|",)
                wr.writerows(self.preds)
        self.lock.release()
        self.preds = []
        print("end-writting", self.idx)

    def run(self):
        print("start-run-thread", self.idx)

        for idx_author in range(self.gap):
            _2hoplist = get_2_hop_u(
                self.G, self.lstNodes[self.startIndex + idx_author])
            preds_by_authorId = nx.adamic_adar_index(self.G, _2hoplist)
            preds_by_authorId = heapq.nlargest(
                self.topK, preds_by_authorId, key=lambda x: x[2])
            for (idx_pred, pred) in enumerate(preds_by_authorId):
                self.preds[idx_author * self.topK + idx_pred] = pred
        print("end-find-adamic_adar", self.idx)

        self.write_csv()
        print("end-run-thread", self.idx)


class Adamic(Algorithm):
    def __init__(self,
                 id=None,

                 descriptions="",
                 valuations={}
                 ):
        super().__init__(name="AdamicAdar", id=id, setting={},
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
        from utils.file import ICON_LINK_PREDICTION
        return ICON_LINK_PREDICTION

    def train(self,
              *arg,
              **kw):
        project_uid = int(kw.get("project_uid"))
        t1 = datetime.now()
        print("start:{0}".format(t1))
        print("start- AdamicAdar", project_uid, self._id)
        self.delete_predictions(project_uid)
        print("delete preiction: Done- AdamicAdar", project_uid, self._id)

        # num_threads = 1000
        lock = Lock()

        from utils.file import deleteFileIfExisted
        deleteFileIfExisted(_temp_file)

        from services.prior_network_service import NetWorkXGraph, get_num_author
        nwx = NetWorkXGraph()
        G = nwx.get_temp_graph()

        lstNodes = list(G.nodes)
        num_author = len(lstNodes)
        gap = 1000
        num_threads = round(num_author / gap)

        print("create threas", num_threads)
        lstThreads = [AdamicAdarThread(
            lock=lock,
            G=G,
            lstNodes=lstNodes,
            startIndex=idx_thread * gap,
            idx=idx_thread,
            gap=get_real_gap(
                num_author, idx_thread * gap, gap),
            topK=10)
            for idx_thread in range(num_threads + 1)]

        for (idx, comThread) in enumerate(lstThreads):
            comThread.start()

        for comThread in lstThreads:
            comThread.join()

        print("done  threads",)
        self._predict(project_uid)
        print("done all predict",)

        t2 = datetime.now()
        print("end:{0}".format(t2))
        print("done",)

    def _predict(self, project_uid: int):
        from utils.file import get_current_directory, connect_path_file
        path = connect_path_file(get_current_directory(neo4j=True), _temp_file)
        query = """
            USING PERIODIC COMMIT 1000
            LOAD CSV FROM $path AS line FIELDTERMINATOR '|'
            WITH line
            
            WITH toInteger(line[0]) AS start_nodeId, 
                 toInteger(line[1]) AS end_nodeId, 
                 toFloat(line[2]) AS score

            MATCH (a:Author ), (b:Author)
            WHERE a.author_id = start_nodeId AND
                b.author_id = end_nodeId AND 
                NOT EXISTS((a)-[:_{uid}_{_id}]->(b))
            CREATE (a)-[:_{uid}_{_id} """.format(uid=project_uid, _id=self._id)
        query += """ {score: score}]->(b)"""
        db.run(query, parameters={"path": path})

    def get_step_list(self):
        step_list = [
            Step(
                name="Bước 1: Tính Adamic Adar từ mỗi cặp nút trong mạng",
                inputs={
                    "CoNet1": "CoNet1",
                },
                outputs={
                    "Tập Adamic Adar": "Tập cặp nút trong mạng kèm Adamic Adar"
                },
                output_file=""),
            Step(
                name="Bước 2: Khuyến nghị theo số Adamic Adar",
                inputs={
                    "Tập Adamic Adar": "Tập Adamic Adar",
                    "topK": 10,
                },
                outputs={
                    "Recommendations": "Danh sách khuyến nghị cho từng nghiên cứu viên"
                },
                output_file=""),
        ]
        return step_list
