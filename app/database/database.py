import os, datetime, json

base_db_template = {
    "hosts_info": {
        "date_created": "yyyy-mm-dd",
        "hosts": {
            "sample_host": {
                "used_size": 0,
            }
        },
    },
}

# simple JSON database
class Database:
    path: str = "./db.json"

    def __init__(self):
        is_db_valid = self.__check_if_valid()
        if not os.path.exists(self.path) or not is_db_valid:
            self.__initialize_db()

        self.__clear_hosts_if_outdated()

    def __get_base_db_template_copy(self) -> dict:
        return json.loads(json.dumps(base_db_template))

    def __check_if_valid(self):
        try:
            db: dict = {}
            with open(self.path, "r") as f:
                db = json.loads(f.read())

            assert "hosts_info" in db.keys()
            assert "date_created" in db["hosts_info"].keys()
            assert "hosts" in db["hosts_info"].keys()

            for host in db["hosts_info"]["hosts"].keys():
                assert "used_size" in db["hosts_info"]["hosts"][host].keys()
                assert type(db["hosts_info"]["hosts"][host]["used_size"]) is int

            return True
        except:
            return False

    def __clear_hosts_if_outdated(self):
        db: dict = None
        with open(self.path, "r") as f:
            db = json.loads(f.read())

        current_date = str(datetime.datetime.now().date())
        if db["hosts_info"]["date_created"] != current_date:
            hosts_info = self.__get_base_db_template_copy()["hosts_info"]
            hosts_info["date_created"] = str(current_date)
            db["hosts_info"] = hosts_info
            self.set_db(db)

    def __initialize_db(self):
        db = self.__get_base_db_template_copy()
        db["hosts_info"]["date_created"] = str(datetime.datetime.now().date())
        with open(self.path, "w+") as f:
            f.write(json.dumps(db))

    def set_db(self, db: dict):
        with open(self.path, "w+") as f:
            f.write(json.dumps(db))

    def get_db(self) -> dict:
        is_db_valid = self.__check_if_valid()
        if not os.path.exists(self.path) or not is_db_valid:
            self.__initialize_db()

        self.__clear_hosts_if_outdated()

        with open(self.path, "r") as f:
            db = json.loads(f.read())
            return db
