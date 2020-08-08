from services.project_service import projectService
from services.neo4j_service import neo4jService
from controllers.excution import excute
from models.project import Project
from models.brief_project import BriefProject


class Controller():
    def __init__(self):
        self.algorithm = None
        self.model = None
        self.training = -1
        """
        + building: dict
        Dùng để chứa {
            uid: ,
            type: "prior"/"test"
        }
        """
        # self.building = None  # dict
        self.authors = None
        self.current = 10
        self.delta = 10
        self.busy = False  # dict

    def get_project_uid(self):
        return 1595426051223

    def get_algorithm_id(self):
        "p= 1.5, q= 0.5"
        return 1596068914007

    def get_author(self, author_id):
        author = neo4jService.get_author(
            author_id=author_id,
            project_uid=self.get_project_uid(),
            model_id=self.get_algorithm_id(),
        )
        return {"author": author}

    def get_list_author(self):
        authors = neo4jService.get_authors(
            self.get_project_uid(),
            self.get_algorithm_id(),
            self.current)
        return {"authors": authors}

    def get_list_recommendations(self, author_id,):
        recommendations = self.algorithm.get_most_similar(
            self.model, author_id)
        recommendations = [neo4jService.get_author(
            author_id=recommendation,
            project_uid=self.get_project_uid(),
            model_id=self.get_algorithm_id(),
            similarity=sim,
            source_id=author_id,
        ) for (recommendation, sim) in recommendations]

        return {"recommendations": recommendations}

    def isConnect(self,) -> bool:
        status = neo4jService.isConnect()
        return status

    def update_algorithm(self):
        uid = self.get_project_uid()
        to_json = projectService.get(uid)
        project = Project()
        project.load(to_json)

        _id = self.get_algorithm_id()
        temp = project.get_algorithm(_id)

        if (temp is None):
            raise ValueError("No model found. Please reconnect to database.")

        from models.node2vec import Node2vec, get_model
        self.algorithm = Node2vec()
        self.algorithm.mapFrom(temp)
        self.model = get_model(self.algorithm.get_output())

    def initNew(self):
        neo4jService.initNew(
            self.get_project_uid(),
            self.get_algorithm_id()
        )


controller = Controller()
