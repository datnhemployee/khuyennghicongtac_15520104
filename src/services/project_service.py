
from utils.file import connect_path_file, PATH_PUBLIC_FOLDER
from models.project import Project
from utils.db import db
import os
import io
import json


class ProjectService():

    def get_connector(self, uid) -> str:
        connector = connect_path_file(
            PATH_PUBLIC_FOLDER, "{0}.json".format(uid))
        return connector

    def has_connector(self, uid) -> bool:
        connector = self.get_connector(uid)
        if (os.path.isfile(connector) and
                os.access(connector, os.R_OK)):
            return True
        return False

    def get(self, uid) -> dict:
        has_connector = self.has_connector(uid)
        data = None
        if (has_connector == False):
            raise ValueError("Không tìm thấy dữ liệu về dự án.")
        else:
            connector = self.get_connector(uid)
            with io.open(connector, 'r') as db_file:
                data = json.load(db_file)

        return data

    # def save(self, algorithm, ) -> int:
    #     """
    #     Public: Hàm gọi khi thêm 1 algorithm vào db
    #     """
    #     data = {
    #         "algorithms": [],
    #         "next_id": 0
    #     }
    #     with io.open(db_algorithms_connector, 'r') as db_file:
    #         data = json.load(db_file)

    #     data["algorithms"].append(algorithm.to_json())
    #     data["next_id"] = int(data["next_id"]) + 1

    #     with io.open(db_algorithms_connector, 'w') as db_file:
    #         db_file.write(json.dumps(data))

    #     return int(data["next_id"])

    def save(self, project, ) -> None:
        """
        Public: Hàm gọi khi thêm 1 algorithm vào db
        """
        data = project.to_json()

        connector = self.get_connector(project.uid)
        with io.open(connector, 'w') as db_file:
            db_file.write(json.dumps(data))


projectService = ProjectService()
