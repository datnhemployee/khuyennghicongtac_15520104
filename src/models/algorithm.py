import copy
from utils.file import DEFAULT_IMAGE as default_icon
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE
from utils.time import get_current_time
from utils.db import db


class Algorithm():
    def __init__(self, name: str, setting: dict, descriptions: str, valuations: dict, id=None):
        self._id = id
        if (id is None):
            self._id = get_current_time()

        self.name = name
        self.setting = copy.deepcopy(setting)
        self.descriptions = descriptions
        self.valuations = {
            "precision": -1,
            "recall": -1,
            "fmeasure": -1,
        }
        for key in self.valuations.keys():
            self.set_valuation(key, valuations.get(key, -1))

    def mapFrom(self, algorithm):
        self.__init__(
            id=self._id,
            name=algorithm.name,
            setting=algorithm.setting,
            descriptions=algorithm.descriptions,
            valuations=algorithm.valuations,
        )

    def to_str_setting(self) -> str:
        result = ""
        for key in self.setting.keys():
            val = self.setting[key]
            result += "{0}: {1}, ".format(key, val)
        return result

    def get_icon_path(self,) -> str:
        return default_icon

    def get_valuation(self, name: str) -> float:
        return self.valuations.get(name, -1)

    def set_valuation(self, name: str, val=-1):
        if (val < 0 or len(name) == 0):
            return False
        self.valuations[name] = val
        return True

    def get_valuation_color(self, name: str) -> str:
        default_color = DARK_BLUE
        if (name == "recall"):
            return BLUE
        elif(name == "fmeasure"):
            return LIGHT_BLUE
        return default_color

    def to_json(self) -> dict:
        result = {
            "_id": self._id,
            "name": self.name,
            "setting": self.setting,
            "descriptions": self.descriptions,
            "valuations": self.valuations,
        }
        return result

    # def train(self,
    #           *arg,
    #           **kw):
    #     project_uid = int(kw.get("project_uid"))
    #     cb_end = kw.get("cb_end", None)
    #     raise ValueError("Không tìm thấy hàm huấn luyện")

    def delete_predictions(self, project_uid):
        query = """
                MATCH (:Author)-[r:_{project_uid}_{algorithm_id}]-(:Author)
                DELETE r
            """.format(project_uid=project_uid, algorithm_id=self._id)
        db.run(query)

    def save(self, recommendation_list: list, project_uid: int,):
        self.delete_predictions(project_uid,)

        if(len(recommendation_list) == 0):
            raise ValueError(
                "Error: No authors were found to make any prediction!!")

        query = """
                MATCH (a:Author),(b:Author)
                WHERE a.author_id=$a_id AND
                    b.author_id=$b_id
                CREATE (a)-[:_{0}_{1} 
            """.format(project_uid, self._id)
        query += "{ top:$top }]->(b)"
        for idx, auth_rec in enumerate(recommendation_list):
            a_id = auth_rec["author_id"]
            for top, b_id in enumerate(auth_rec["topK"]):
                # print("a_id", a_id, "b_id", b_id)
                if (b_id > 0):
                    db.run(query, parameters={
                        "a_id": a_id, "b_id": b_id, "top": top})

    def valuate(self, project_uid: int) -> dict:
        true_positive = 0
        false_positive = 10
        false_negative = 10

        precision = 0
        recall = 0
        f_measure = 0

        """
            true_positive: Số liên kết thật sự đúng nhưng không được tiên đoán

                1.Tìm số liên kết cần tiên đoán tại mỗi nút num_col,  num_col <= 5
                2.Số liên kết thật sự đúng và được chưa tiên đoán trong giới hạn num_col =
                    num_col - Số liên kết thật sự đúng và được tiên đoán trong giới hạn num_col
            """
        query = """
                MATCH (a:Author)-[r:_{0}_{1}]->(lily:Author)
                WHERE a.test_{0} = TRUE
                    AND EXISTS((a)-[:test_{0}]-(lily))
                RETURN COUNT(r) AS tp
                """.format(project_uid, self._id)
        for idx, row in enumerate(db.run(query,)):
            true_positive = row[0]

        """
            false_positive: Số liên kết không đúng nhưng vẫn được tiên đoán

                + lấy số liên kết cần tiên đoán tại mỗi nút
                + xem trong topk' với k'<5 và k'=số liên kết cần tiên đoán tại mỗi nút,
                    có bao nhiêu tiên đoán sai

                    MATCH (a:Author)-[r:test_{0}]-(b:Author)
                    WITH DISTINCT a, COUNT(DISTINCT b.author_id) AS num_col
                    
                    MATCH (a)-[r:_{0}_{1}]->(lily:Author)
                    WHERE a.test_{0} = TRUE
                        AND r.top < num_col
                        AND NOT EXISTS((a)-[:test_{0}]-(lily))
                    RETURN COUNT(r) AS fp
            """
        query = """
                    MATCH (a:Author)-[r:_{0}_{1}]->(lily:Author)
                    WHERE a.test_{0} = TRUE
                        AND NOT EXISTS((a)-[:test_{0}]-(lily))
                    RETURN COUNT(r) AS fp
                    """.format(project_uid, self._id)
        for idx, row in enumerate(db.run(query,)):
            false_positive = row[0]

        """
            false_negative: Số liên kết thật sự đúng nhưng không được tiên đoán

                1.Tìm số liên kết cần tiên đoán tại mỗi nút num_col,  num_col <= TopK
                2.Số liên kết thật sự đúng và được chưa tiên đoán trong giới hạn num_col =
                    min(num_col, TopK) - Số liên kết thật sự đúng và được tiên đoán trong giới hạn num_col
            """
        query = """
                MATCH (a:Author)-[r:test_{0}]-(lily:Author)
                WHERE a.test_{0} = TRUE
                    AND NOT EXISTS((a)-[:_{0}_{1}]->(lily))
                RETURN COUNT(r) AS fn
                """.format(project_uid, self._id)
        for idx, row in enumerate(db.run(query,)):
            false_negative = row[0]

        print("true_positive", true_positive, "false_positive",
              false_positive, "false_negative", false_negative)
        precision = true_positive * 1.0/(true_positive + false_positive)
        recall = true_positive * 1.0/(true_positive + false_negative)
        f_measure = 2*precision * recall * 1.0/(precision + recall)
        print("precision", precision, "recall", recall, "f_measure", f_measure)

        self.valuations = {
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "fmeasure": round(f_measure, 2),
        }

        return copy.deepcopy(self.valuations)

    def set_setting(self, title, val):
        self.setting[title] = val

    def get_step_list(self):

        return []
