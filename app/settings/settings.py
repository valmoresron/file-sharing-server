import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    secret_key = os.getenv("SECRET_KEY")

    def __init__(self) -> None:
        self._test()

    def _test(self):
        try:
            assert isinstance(self.secret_key, str)
        except:
            raise AssertionError("Secret key must be a string")
