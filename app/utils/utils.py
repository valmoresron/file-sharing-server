import os, hashlib, hmac

from fastapi import UploadFile
from app.common import settings

secret_key = settings.secret_key
savepath = "./files"  # TODO Add in .env

os.makedirs(savepath, exist_ok=True)


class FileUploadHandler:
    file: UploadFile
    file_contents: bytes
    public_key: str
    private_key: str

    def __init__(self, file: UploadFile):
        self.file = file
        self.file_contents = file.file.read()
        self.private_key = ""
        self.public_key = ""
        self.__calculate_public_key()
        self.__calculate_private_key()

    def __calculate_public_key(self):
        if not self.public_key:
            hash = hashlib.sha256(self.file_contents)
            public_key = hash.hexdigest()
            self.public_key = public_key

    def __calculate_private_key(self):
        if not self.private_key:
            self.__calculate_public_key()
            public_key = self.public_key
            digestmod = "sha256"
            private_key = hmac.new(
                key=secret_key.encode(),
                msg=public_key.encode(),
                digestmod=digestmod,
            ).hexdigest()
            self.private_key = private_key

    def save_file(self):
        uploaded_filename = self.file.filename
        save_filename = self.public_key + uploaded_filename
        save_filepath = os.path.join(savepath, save_filename)

        with open(save_filepath, "wb") as f:
            f.write(self.file_contents)


def get_saved_filenames() -> list[str]:
    filenames = [f for f in os.listdir(savepath) if os.path.isfile(os.path.join(savepath, f))]
    return filenames

def get_saved_filepath(saved_filename: str) -> str:
    return os.path.join(savepath, saved_filename)