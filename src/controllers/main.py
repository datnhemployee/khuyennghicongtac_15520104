from services.project_service import projectService
from services.database_service import databaseService
from services.neo4j_service import neo4jService
from controllers.excution import excute
from models.project import Project
from models.brief_project import BriefProject
from models.database import Database


class Controller():
    def __init__(self):
        self.database = Database()
        self.project = Project()
        self.training = -1
        """
        + building: dict
        Dùng để chứa {
            uid: ,
            type: "prior"/"test"
        }
        """
        # self.building = None  # dict
        self.busy = False  # dict

    def isInit(self, callback, on_error):
        excute(task=neo4jService.isInited,
               callback=callback,
               on_error=on_error)

    def init(self, callback, on_error):
        excute(task=neo4jService.initNew,
               callback=lambda **kw: callback(),
               on_error=on_error)

    def get_algorithm(self, _id: int):
        return self.project.get_algorithm(_id)

    def get_project(self, uid):
        to_json = projectService.get(uid)
        self.project.load(to_json)

    def get_all_projects(self,):
        to_json = databaseService.load()
        self.database.load(to_json)

    def _add_project(
        self,
        name: str,
        prior_start: int,
        prior_end: int,
        test_start: int,
        test_end: int,
    ):
        try:
            prior_start = int(prior_start)
            prior_end = int(prior_end)
            test_start = int(test_start)
            test_end = int(test_end)
        except:
            self.busy = False
            raise ValueError(
                "Một số trường dữ liệu bị sai. Vui lòng kiểm  tra lại.")
        if (prior_start < 1995 or
                prior_end < 1995 or
                test_end < 1995 or
                test_end < 1995 or
                prior_start > prior_end or
                test_start > test_end or
                prior_end > test_start
            ):
            self.busy = False
            raise ValueError(
                "Cơ sở dữ liệu phải thiết lập sau 1995 và tập huấn luyện phải trước tập tập đánh giá.")

        result = Project(name=name)
        is_prior_init = neo4jService.is_init(result.uid, "prior")
        if (is_prior_init == False):
            neo4jService.init_prior(
                result.uid,
                prior_start,
                prior_end
            )
            neo4jService.init_test(
                result.uid,
                test_start,
                test_end
            )

        result.set_prior_num_author(neo4jService.get_num_author(
            result.uid, "prior"))
        result.set_prior_num_paper(neo4jService.get_num_paper(
            result.uid, "prior"))
        result.set_prior_num_connection(neo4jService.get_num_connection(
            result.uid, "prior"))

        result.set_test_num_author(neo4jService.get_num_author(
            result.uid, "test"))
        result.set_test_num_connection(neo4jService.get_num_prediction(
            result.uid))

        result.set_test_graph_num_author(neo4jService.get_num_test_graph_author(
            result.uid,))
        result.set_test_graph_num_paper(neo4jService.get_num_paper(
            result.uid, "test"))
        result.set_test_graph_num_connection(neo4jService.get_num_connection(
            result.uid, "test"))

        projectService.save(result)
        self.database.add(result.to_json())
        databaseService.save(self.database)
        self.busy = False

    def add_project(
        self,
        name: str,
        prior_start: int,
        prior_end: int,
        test_start: int,
        test_end: int,
        callback=None,
        on_error=None,
    ):
        if (self.busy == False):
            self.busy = True
            excute(
                task=self._add_project,
                callback=callback,
                args={
                    "name": name,
                    "prior_start": prior_start,
                    "prior_end": prior_end,
                    "test_start": test_start,
                    "test_end": test_end,
                },
                on_error=on_error
            )
        else:
            self.busy = False
            on_error(ValueError(
                "Đang dùng tài nguyên thực hiện 1 hành động tính toán khác. Vui lòng đợi"))

    def add_algorithm(self, algorithm):
        self.project.add_algorithm(algorithm)
        projectService.save(self.project)

    def is_trained(self, algorithm) -> bool:
        return neo4jService.is_trained(self.project.uid, algorithm._id)

    def _train(self, algorithm, **kwargs):
        algorithm.train(project_uid=self.project.uid)
        self.project.update_algorithm(algorithm)
        projectService.save(self.project)
        self.busy = False

    def train(self, algorithm, on_error=None, callback=None, **kwargs):
        if(self.busy == False):
            self.busy = True
            kwargs["algorithm"] = algorithm
            excute(task=self._train, on_error=on_error,
                   args=kwargs, callback=callback)
        else:
            on_error(ValueError(
                "Chỉ có thể huấn luyện/ đánh giá 1 mô hình tại 1 thời điểm."))

    def _valuate(self, algorithm, callback=None, **kw):
        algorithm.valuate(project_uid=self.project.uid)
        self.project.update_algorithm(algorithm)
        projectService.save(self.project)
        self.busy = False

    def valuate(self, algorithm, on_error=None, callback=None, **kw):
        if(self.busy == False):
            self.busy = True
            kw["project_uid"] = self.project.uid
            kw["algorithm"] = algorithm
            excute(task=self._valuate, on_error=on_error,
                   callback=callback, args=kw)
        else:
            on_error(ValueError(
                "Chỉ có thể huấn luyện/ đánh giá 1 mô hình tại 1 thời điểm."))

    def mapAlgorithm(self, algorithm):
        if (algorithm is not None):
            if (algorithm.name == "Node2vec"):
                from models.node2vec import Node2vec
                result = Node2vec()
                result.mapFrom(algorithm)
                return result
            if (algorithm.name == "CommonNeighbor"):
                from models.common_neighbor import CommonNeighbor
                result = CommonNeighbor()
                result.mapFrom(algorithm)
                return result
            if (algorithm.name == "Jaccard"):
                from models.jaccard import Jaccard
                result = Jaccard()
                result.mapFrom(algorithm)
                return result
            if (algorithm.name == "AdamicAdar"):
                from models.adamic import Adamic
                result = Adamic()
                result.mapFrom(algorithm)
                return result
            if (algorithm.name == "ContentBased"):
                from models.content_based import ContentBased
                result = ContentBased()
                result.mapFrom(algorithm)
                return result
        return algorithm

    def openReport(self):
        import webbrowser
        from utils.file import FILE_REPORT
        webbrowser.open_new(FILE_REPORT)

    def openInstruction(self):
        import webbrowser
        from utils.file import FILE_INTRODUCTION
        webbrowser.open_new(FILE_INTRODUCTION)


controller = Controller()
