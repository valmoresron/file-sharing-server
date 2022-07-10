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

# this database is used to track how much size the client with the same IP has used
# it uses a JSON file to keep the records
class Database:
    path: str = "./db.json"  # static path to the JSON database

    # contructor; check database file validity
    def __init__(self):
        is_db_valid = self.__check_if_valid()
        if not os.path.exists(self.path) or not is_db_valid:
            self.__initialize_db()

        self.__clear_hosts_if_outdated()

    # creates a deep copy of the base_db_template variable; this serves as the database template
    def __get_base_db_template_copy(self) -> dict:
        return json.loads(json.dumps(base_db_template))

    # checks the database for corruption; asserts that all properties exist; crude way of type checking
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

    # if the hosts_info's date of creation does not match the current date,
    # it remove all the records to reset the client's upload and download limits
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

    # initializes the database file
    def __initialize_db(self):
        db = self.__get_base_db_template_copy()
        db["hosts_info"]["date_created"] = str(datetime.datetime.now().date())
        with open(self.path, "w+") as f:
            f.write(json.dumps(db))

    # writes the passed database value to the file
    def set_db(self, db: dict):
        with open(self.path, "w+") as f:
            f.write(json.dumps(db))

    # performs checks and returns the database from the JSON files
    def get_db(self) -> dict:
        is_db_valid = self.__check_if_valid()
        if not os.path.exists(self.path) or not is_db_valid:
            self.__initialize_db()

        self.__clear_hosts_if_outdated()

        with open(self.path, "r") as f:
            db = json.loads(f.read())
            return db

    # deletes the database file and creates a new one
    def reset_database(self):
        if os.path.exists(self.path) and os.path.isfile(self.path):
            os.remove(self.path)
            self.__initialize_db()
