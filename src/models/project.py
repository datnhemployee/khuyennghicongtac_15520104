from models.brief_project import BriefProject
from models.algorithm import Algorithm
from utils.time import get_current_time
from copy import deepcopy


class Project(BriefProject):
    def __init__(self,
                 uid=None,
                 name="Tên dự án",
                 algorithms=[],
                 next_id=0,
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
        super().__init__(uid, name, prior, test)
        self.next_id = next_id
        self.algorithms = algorithms

    def load(self, data: dict):
        super().load(data)

        next_id = data.get("next_id", 0)

        algorithms = data.get("algorithms", [])

        self.next_id = int(next_id)
        self.algorithms = [
            Algorithm(
                id=algorithm.get("_id"),
                name=algorithm.get("name"),
                descriptions=algorithm.get("descriptions"),
                setting=algorithm.get("setting"),
                valuations=algorithm.get("valuations"),
            )
            for algorithm in algorithms]

    def to_json(self) -> dict:
        result = {
            "uid": self.uid,
            "name": self.name,
            "algorithms": [algorithm.to_json() for algorithm in self.algorithms],
            "next_id": self.next_id,
            "prior": deepcopy(self.prior),
            "test": deepcopy(self.test),
        }
        return result

    def add_algorithm(self, algorithm):
        self.algorithms.append(algorithm)

    def update_algorithm(self, algorithm):
        for _algorithm in self.algorithms:
            if (_algorithm._id == algorithm._id):
                _algorithm.mapFrom(algorithm)

    def get_algorithm(self, _id: int):
        for _algorithm in self.algorithms:
            if (_algorithm._id == _id):
                return _algorithm
        return None
