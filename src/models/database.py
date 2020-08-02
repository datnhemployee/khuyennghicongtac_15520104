from models.brief_project import BriefProject


class Database():
    def __init__(self):
        self.projects = []

    def load(self, data: dict):
        self.projects = []
        _projects = data.get("projects", [])

        for _project in _projects:
            self.add(_project)

    def add(self, data: dict):
        _temp = BriefProject()
        _temp.load(data)
        self.projects.append(_temp)

    def to_json(self,):
        result = {
            "projects": [briedProject.to_json() for briedProject in self.projects]
        }
        return result
