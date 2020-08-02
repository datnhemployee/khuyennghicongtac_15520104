from models.algorithm import Algorithm
from utils.db import db

from models.step import Step

from threading import Thread, Lock
import csv
import networkx as nx
import heapq
from datetime import datetime

_temp_katz = "public/katz.csv"
_temp_file = _temp_katz


def katz(G, author_id: int, length=10, beta=0.85) -> list:
    if (author_id is None or G is None):
        raise ValueError("Không thể chạy với author_id rỗng và G rỗng.")

    result = []
    dict_katz = {}
    neighbors = nx.neighbors(G, author_id)
    for neighbor in neighbors:
        dict_katz[neighbor] = beta
    l = 1
    next_neighs = neighbors
    while l <= length:
        _temp_neighs = []
        for neighbor in next_neighs:
            for friend in nx.neighbors(neighbor):
                _temp_neighs.append(friend)

        for neighbor in _temp_neighs:
            num_path = _temp_neighs.count(neighbor)
            if (num_path > 0):
                if (dict_katz.get(neighbor, None) is None):
                    dict_katz[neighbor] = num_path * (beta**l)
                else:
                    dict_katz[neighbor] += num_path * (beta**l)

        next_neighs = _temp_neighs
        l += 1

    result = [(author_id, key, dict_katz[key]) for key in dict_katz.keys()]

    return result


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


class KatzThread(Thread):
    def __init__(self,
                 lock,
                 G,
                 lstNodes: list,
                 startIndex: int,
                 gap: int,
                 beta: float,
                 topK: int,
                 idx: int
                 ):
        Thread.__init__(self)
        self.lstNodes = lstNodes
        self.lock = lock
        self.startIndex = startIndex
        self.gap = gap
        self.beta = beta
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
            preds_by_authorId = katz(
                self.G, self.lstNodes[idx_author], length=10, beta=self.beta)
            preds_by_authorId = heapq.nlargest(
                self.topK, preds_by_authorId, key=lambda x: x[2])
            for (idx_pred, pred) in enumerate(preds_by_authorId):
                self.preds[idx_author * self.topK + idx_pred] = pred
        print("end-find-katz", self.idx)

        self.write_csv()
        print("end-run-thread", self.idx)


class Katz(Algorithm):
    def __init__(self,
                 id=None,
                 beta=0.85,
                 descriptions="",
                 valuations={}
                 ):
        super().__init__(name="Katz", id=id, setting={
            "beta": beta
        },
            descriptions=descriptions,
            valuations=valuations)

    def mapFrom(self, algorithm: Algorithm):
        self.__init__(
            id=algorithm._id,
            beta=float(algorithm.setting["beta"]),
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

        self.delete_predictions(project_uid)
        t1 = datetime.now()
        print("start:{0}".format(t1))
        print("start- katz", project_uid)
        # num_threads = 1000
        # lock = Lock()

        # from utils.file import deleteFileIfExisted
        # deleteFileIfExisted(_temp_file)

        # from services.prior_network_service import NetWorkXGraph, get_num_author
        # nwx = NetWorkXGraph()
        # G = nwx.get_temp_graph()

        # # num_author = 100000
        # lstNodes = list(G.nodes)
        # num_author = len(lstNodes)
        # # print("start- num_author1", num_author)
        # # lstNodes = lstNodes[:num_author]
        # # num_author = get_num_author(project_uid, "prior")
        # # print("start- num_author2", num_author)
        # # print("num_author", lstNodes)
        # # gap = int(num_author / num_threads)
        # gap = 1000
        # num_threads = round(num_author / gap)

        # print("create threads", num_threads)
        # lstThreads = [KatzThread(
        #     lock=lock,
        #     G=G,
        #     lstNodes=lstNodes,
        #     startIndex=idx_thread * gap,
        #     idx=idx_thread,
        #       beta = self.beta,
        #     gap=get_real_gap(
        #         num_author, idx_thread * gap, gap),
        #     topK=10)
        #     for idx_thread in range(num_threads + 1)]

        # for (idx, comThread) in enumerate(lstThreads):
        #     comThread.start()

        # for comThread in lstThreads:
        #     comThread.join()

        print("done all threads",)
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

            MATCH (a:Author), (b:Author)
            WHERE a.author_id = start_nodeId AND
                b.author_id = end_nodeId AND 
                NOT EXISTS((a)-[:_{uid}_{_id}]->(b))
            CREATE (a)-[:_{uid}_{_id} """.format(uid=project_uid, _id=self._id)
        query += """ {score: score}]->(b)"""
        db.run(query, parameters={"path": path})

    def get_step_list(self):
        step_list = [
            Step(
                name="Bước 1: Tính Katz từ mỗi cặp nút trong mạng",
                inputs={
                    "CoNet1": "CoNet1",
                    "beta": 0.85,
                },
                outputs={
                    "Tập Katz": "Tập cặp nút trong mạng kèm Katz"
                },
                output_file=""),
            Step(
                name="Bước 2: Khuyến nghị theo số Katz",
                inputs={
                    "Tập Katz": "Tập Katz",
                    "topK": 10,
                },
                outputs={
                    "Recommendations": "Danh sách khuyến nghị cho từng nghiên cứu viên"
                },
                output_file=""),
        ]
        return step_list
