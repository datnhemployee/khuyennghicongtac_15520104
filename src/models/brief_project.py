from utils.time import get_current_time
from copy import deepcopy


class BriefProject():
    def __init__(self,
                 uid=None,
                 name="Tên dự án",
                 prior={
                     "start": 2014,
                     "end": 2015,
                     "num_author": 0,
                     "num_paper": 0,
                     "num_connection": 0,
                 },
                 test={
                     "start": 2016,
                     "end": 2016,
                     "num_author": 0,
                     "num_connection": 0,
                     "num_graph_author": 0,
                     "num_graph_paper": 0,
                     "num_graph_connection": 0,
                 },
                 ):
        if(uid is None):
            self.uid = get_current_time()
        else:
            self.uid = uid
        self.name = name
        self.prior = deepcopy(prior)
        self.test = deepcopy(test)

    def load(self, data: dict):

        uid = data.get("uid", None)
        if(uid is None):
            self.uid = get_current_time()
        else:
            self.uid = uid

        name = data.get("name", None)
        if(name is None):
            raise ValueError("Lỗi tệp dự án.")

        prior = data.get("prior", None)
        if(prior is None):
            raise ValueError("Lỗi tệp dự án.")

        test = data.get("test", None)
        if(test is None):
            raise ValueError("Lỗi tệp dự án.")

        self.name = name
        self.prior = deepcopy(prior)
        self.test = deepcopy(test)

    def get_prior_start(self) -> int:
        return self.prior["start"]

    def get_prior_end(self) -> int:
        return self.prior["end"]

    def get_test_start(self) -> int:
        return self.test["start"]

    def get_test_end(self) -> int:
        return self.test["end"]

    def get_prior_num_author(self) -> int:
        return self.prior["num_author"]

    def get_prior_num_paper(self) -> int:
        return self.prior["num_paper"]

    def get_prior_num_connection(self) -> int:
        return self.prior["num_connection"]

    def get_test_num_author(self) -> int:
        return self.test["num_author"]

    def get_test_num_connection(self) -> int:
        return self.test["num_connection"]

    def get_test_graph_num_author(self) -> int:
        return self.test["num_graph_author"]

    def get_test_graph_num_paper(self) -> int:
        return self.test["num_graph_paper"]

    def get_test_graph_num_connection(self) -> int:
        return self.test["num_graph_connection"]

    def set_prior_start(self, val: int):
        self.prior["start"] = val

    def set_prior_end(self, val: int):
        self.prior["end"] = val

    def set_test_start(self, val: int):
        self.test["start"] = val

    def set_test_end(self, val: int):
        self.test["end"] = val

    def set_prior_num_author(self, val: int):
        self.prior["num_author"] = val

    def set_prior_num_paper(self,  val: int):
        self.prior["num_paper"] = val

    def set_prior_num_connection(self,  val: int):
        self.prior["num_connection"] = val

    def set_test_num_author(self,  val: int):
        self.test["num_author"] = val

    def set_test_num_paper(self,  val: int):
        self.test["num_paper"] = val

    def set_test_num_connection(self,  val: int):
        self.test["num_connection"] = val

    def set_test_graph_num_author(self,  val: int):
        self.test["num_graph_author"] = val

    def set_test_graph_num_paper(self,  val: int):
        self.test["num_graph_paper"] = val

    def set_test_graph_num_connection(self,  val: int):
        self.test["num_graph_connection"] = val

    def to_json(self) -> dict:
        result = {
            "uid": self.uid,
            "name": self.name,
            "prior": deepcopy(self.prior),
            "test": deepcopy(self.test),
        }
        return result
