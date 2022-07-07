import os, hashlib, hmac

from fastapi import UploadFile
from app.common import settings

secret_key = settings.secret_key
filespath = "./files"  # TODO Add in .env


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
        os.makedirs(filespath, exist_ok=True)
        uploaded_filename = self.file.filename
        save_filename = self.public_key + uploaded_filename
        save_filepath = os.path.join(filespath, save_filename)

        with open(save_filepath, 'wb') as f:
            f.write(self.file_contents)

