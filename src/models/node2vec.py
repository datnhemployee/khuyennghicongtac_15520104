from models.algorithm import Algorithm
from services.prior_network_service import NetWorkXGraph, get_all_author_id, get_num_author
from utils.file import get_path_node2vec_emb, existing_file
from utils.db import db
import csv
from threading import Thread, Lock

from models.step import Step


_temp_node2vec = "public/node2vec1.csv"
_temp_file = _temp_node2vec


def get_model(path_csv, ):
    from gensim.models import KeyedVectors
    model = KeyedVectors.load_word2vec_format(path_csv)
    return model


def get_real_gap(num_authors: int, startIndex: int, gap: int) -> int:
    num_scan = num_authors - startIndex - gap
    if (num_scan > 0):
        return gap
    return max([num_authors - startIndex, 0])


class Node2vec(Algorithm):
    def __init__(self,
                 id=None,

                 p=1.0,
                 q=1.0,

                 num_walks=10,
                 walk_length=80,

                 dimensions=128,
                 window_size=5,

                 descriptions="",
                 valuations={}
                 ):
        super().__init__(name="Node2vec", id=id, setting={
            "p": p,
            "q": q,
            "num_walks": num_walks,
            "walk_length": walk_length,
            "dimensions": dimensions,
            "window_size": window_size, },
            descriptions=descriptions,
            valuations=valuations)
        self.p = p
        self.q = q
        self.num_walks = num_walks
        self.walk_length = walk_length
        self.dimensions = dimensions
        self.window_size = window_size

    def mapFrom(self, algorithm: Algorithm):
        self.__init__(
            id=algorithm._id,
            p=float(algorithm.setting["p"]),
            q=float(algorithm.setting["q"]),
            num_walks=int(algorithm.setting["num_walks"]),
            walk_length=int(algorithm.setting["walk_length"]),
            dimensions=int(algorithm.setting["dimensions"]),
            window_size=int(algorithm.setting["window_size"]),
            descriptions=algorithm.descriptions,
            valuations=algorithm.valuations,
        )

    def _walk(self, project_uid: int) -> list:
        nx_G = NetWorkXGraph(
            p=self.p, q=self.q)
        nx_G.create(project_uid=project_uid)
        walks = nx_G.simulate_walks(
            num_walks=self.num_walks, walk_length=self.walk_length)
        return walks

    def get_output(self) -> str:
        output = get_path_node2vec_emb(self._id)
        return output

    def get_icon_path(self):
        from utils.file import ICON_NODE2VEC
        return ICON_NODE2VEC

    def train(self,
              *arg,
              **kw
              ):
        print("Node2vec-start")
        workers = 8
        num_iteration = 1
        project_uid = int(kw.get("project_uid"))
        cb_end = kw.get("cb_end", None)
        # cb_walk = kw.get("cb_walk", None)
        # cb_emb = kw.get("cb_emb", None)

        output = self.get_output()
        walks = self._walk(project_uid)

        self._learn_embedding(
            output,
            walks,
            self.dimensions,
            self.window_size,
            workers,
            num_iteration,
        )
        # release walks
        walks = None

        # recommendation_list = self._predict(uid=project_uid)
        # self.save(recommendation_list=recommendation_list,
        #           project_uid=project_uid)

        print("Node2vec-export")
        self.export(uid=project_uid)
        print("Node2vec-predict")
        self._predict(project_uid=project_uid)

        if (cb_end is not None):
            cb_end()
        print("Node2vec-end")

    def _learn_embedding(
            self,
            output=None,
            walks=[],
            dimensions=128,
            window_size=10,
            workers=8,
            iter=1
    ):
        '''
        Learn embeddings by optimizing the Skipgram objective using SGD.
        '''
        from gensim.models import Word2Vec

        """
        + Bug: TypeError: object of type 'map' has no len()
        + Reason: (Python2.map()) <> (Python3.map())
            Because python2's map function is different from python3's.
            Try to modify line 86 in main.py to walks = [list(map(str, walk)) for walk in walks]
            If you run main.py with python2,it worked without modifying the code
        + Fix:
        see also: https://github.com/aditya-grover/node2vec/issues/35
        """
        # walks = [list(map(str, walk)) for walk in walks]
        model = Word2Vec(walks, size=dimensions, window=window_size,
                         min_count=0, sg=1, workers=workers, iter=iter,)
        model.wv.save_word2vec_format(output)

    # def get_model(self, ):
    #     output = self.get_output()
    #     from gensim.models import KeyedVectors
    #     model = KeyedVectors.load_word2vec_format(output)
    #     return model

    def get_most_similar(self, model, author_id: str, topn=10) -> list:
        result = model.most_similar(
            positive=[author_id], negative=[], topn=topn)
        return result

    def _predict(self, project_uid: int):
        from utils.file import get_current_directory, connect_path_file
        path = connect_path_file(get_current_directory(neo4j=True), _temp_file)
        query = """
            USING PERIODIC COMMIT 5000
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

    def export(self, uid: int):
        self.delete_predictions(uid)
        # print("multithread")
        lockGetModel = Lock()
        lockWrite = Lock()

        from utils.file import deleteFileIfExisted
        deleteFileIfExisted(_temp_file)

        topK = 10
        lstNodes = get_all_author_id(uid, "prior")
        num_author = len(lstNodes)
        preds = [(-1, -1, -1) for authorIdx in range(num_author * topK)]

        gap = 10000
        # gap = 30000
        num_threads = round(num_author / gap)

        print("create threas", num_threads)

        class Node2vecThread(Thread):
            def __init__(self,
                         lockGetModel,
                         lockWrite,
                         #  most_sim,
                         #  lstNodes: list,
                         path_model,
                         startIndex: int,
                         gap: int,
                         topK: int,
                         idx: int
                         ):
                Thread.__init__(self)
                # self.lstNodes = lstNodes
                self.lockGetModel = lockGetModel
                self.lockWrite = lockWrite
                self.startIndex = startIndex
                self.gap = gap
                self.path_model = path_model
                # self.most_sim = most_sim
                self.idx = idx
                self.topK = topK

                self.preds = [(-1, -1, -1.0)
                              for author_idx in range(10 * self.gap)]

                print("run-", self.startIndex, self.gap,)

            def write_csv(self):
                print("start-writting", self.idx)
                from utils.file import existing_file
                self.lockWrite.acquire()
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
                self.lockWrite.release()
                self.preds = []
                print("end-writting", self.idx)

            def run(self):
                print("start-run-thread", self.idx)
                self.lockGetModel.acquire()
                model = get_model(self.path_model)
                self.lockGetModel.release()
                print("end-get-model", self.idx)

                for idx_author in range(self.gap):
                    # author_id = self.lstNodes[self.startIndex + idx_author]
                    author_id = lstNodes[self.startIndex + idx_author]
                    preds_by_authorId = model.most_similar(
                        positive=[str(author_id)], negative=[], topn=self.topK)
                    preds_by_authorId = [(author_id, int(_author_id), sim)
                                         for (_author_id, sim) in preds_by_authorId]
                    for (idx_pred, pred) in enumerate(preds_by_authorId):
                        self.preds[idx_author *
                                   self.topK + idx_pred] = pred

                print("end-find-10-most--all", self.idx)

                self.write_csv()
                print("end-run-thread", self.idx)

        lstThreads = [Node2vecThread(
            lockGetModel=lockGetModel,
            lockWrite=lockWrite,
            # most_sim=model.most_similar,
            # lstNodes=lstNodes,
            path_model=self.get_output(),
            startIndex=idx_thread * gap,
            idx=idx_thread,
            gap=get_real_gap(
                num_author, idx_thread * gap, gap),
            topK=10)
            for idx_thread in range(num_threads + 1)]

        for (idx, _thread) in enumerate(lstThreads):
            _thread.start()

        for _thread in lstThreads:
            _thread.join()

    # def _predict(self, uid: int, TopK=10, ) -> list:

    #     model = self.get_model()
    #     list_author = get_all_author_id(uid=uid, type_db="test")
    #     recommendation_list = [{"author_id": 0, "topK": [-1 for topk in range(TopK)]}
    #                            for auth in list_author]

    #     for idx, author_id in enumerate(list_author):
    #         # print("author_id", author_id)
    #         author_id = author_id
    #         recommendation_list[idx]["author_id"] = author_id
    #         most_sim = self.get_most_similar(model, str(author_id), TopK)
    #         for topk, auth_id in enumerate(most_sim):
    #             recommendation_list[idx]["topK"][topk-1] = int(auth_id[0])
    #             # print("auth_id[0]", auth_id[0])

    #     return recommendation_list

    def set_setting(self, title, val):
        if (title not in self.setting):
            return False

        if (title in ["p", "q"]):
            try:
                val = float(val)
                if (val <= 0):
                    raise ValueError("")
            except:
                raise ValueError("p và q phải mang giá trị số thực dương.")
        elif (title in ["num_walks", "walk_length", "dimensions", "window_size"]):
            try:
                val = int(float(val))
                if (val <= 0):
                    raise ValueError("")
            except:
                raise ValueError(
                    "num_walks, walk_length, dimensions và window_size phải mang giá trị số nguyên dương.")
        super().set_setting(title, val)
        setattr(self, title, val)

    def get_step_list(self):
        step_list = [
            Step(
                name="Bước 1: Bước ngẫu nhiên từ mỗi nút trong mạng",
                inputs={
                    "CoNet1": "CoNet1",
                    "walk_length": self.setting["walk_length"],
                    "num_walks": self.setting["num_walks"],
                    "p": self.setting["p"],
                    "q": self.setting["q"],
                },
                outputs={
                    "Walks": "Tập bước ngẫu nhiên từ mọi nút trong mạng"
                },
                output_file=""),
            Step(
                name="Bước 2: Ánh xạ nút vào không gian vectơ",
                inputs={
                    "Walks": "Walks",
                    "dimensions": self.setting["dimensions"],
                    "window_size": self.setting["window_size"],
                },
                outputs={
                    "Vectơ đặc trưng": "Vectơ đặc trưng của từng nút"
                },
                output_file=""),
            Step(
                name="Bước 3: Khuyến nghị theo vectơ đặc trưng",
                inputs={
                    "Vectơ đặc trưng": "Vectơ đặc trưng",
                    "topK": 10,
                },
                outputs={
                    "Recommendations": "Danh sách khuyến nghị cho từng nghiên cứu viên"
                },
                output_file="")
        ]
        return step_list
