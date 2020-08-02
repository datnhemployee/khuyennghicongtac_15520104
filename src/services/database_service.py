from utils.file import PATH_DATABASE, existing_file
import io
import json


class DatabaseService():
    def __init__(self):
        """
        Chưa cần khởi tạo 
        """

    def load(self) -> dict:
        """
        Lấy từ db.json
        """
        result = {
            "projects": []
        }
        is_existed = existing_file(PATH_DATABASE)
        if (is_existed != True):
            with io.open(PATH_DATABASE, 'w') as db_file:
                db_file.write(json.dumps(result))
        else:
            with io.open(PATH_DATABASE, 'r') as db_file:
                result = json.load(db_file)
        return result

    def save(self, database) -> None:
        """
        Thêm vào db.json
        """
        to_json = database.to_json()
        with io.open(PATH_DATABASE, 'w') as db_file:
            db_file.write(json.dumps(to_json))


databaseService = DatabaseService()
