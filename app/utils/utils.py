import os, hashlib, hmac

from fastapi import UploadFile
from app.common import settings

secret_key = settings.secret_key
savepath = "./files"  # TODO Add in .env

os.makedirs(savepath, exist_ok=True)


class CryptoHandler:
    def calculate_public_key(self, contents: bytes) -> str:
        hash = hashlib.sha256(contents)
        public_key = hash.hexdigest()
        return public_key

    def calculate_private_key(self, message: str) -> str:
        digestmod = "sha256"
        private_key = hmac.new(
            key=secret_key.encode(),
            msg=message.encode(),
            digestmod=digestmod,
        ).hexdigest()
        return private_key


class FileUploadHandler:
    file: UploadFile
    file_contents: bytes
    public_key: str
    private_key: str
    crypto_handler: CryptoHandler

    def __init__(self, file: UploadFile):
        self.file = file
        self.file_contents = file.file.read()
        self.private_key = ""
        self.public_key = ""
        self.crypto_handler = CryptoHandler()
        self.__calculate_public_key()
        self.__calculate_private_key()

    def __calculate_public_key(self):
        if not self.public_key:
            file_contents = self.file_contents
            public_key = self.crypto_handler.calculate_public_key(file_contents)
            self.public_key = public_key

    def __calculate_private_key(self):
        if not self.private_key:
            self.__calculate_public_key()
            public_key = self.public_key
            private_key = self.crypto_handler.calculate_private_key(public_key)
            self.private_key = private_key

    def save_file(self):
        uploaded_filename = self.file.filename
        save_filename = self.public_key + uploaded_filename
        save_filepath = os.path.join(savepath, save_filename)

        with open(save_filepath, "wb") as f:
            f.write(self.file_contents)


class SavedFilesHandler:
    crypto_handler: CryptoHandler

    def __init__(self) -> None:
        self.crypto_handler = CryptoHandler()

    def get_saved_filenames(self) -> str:
        filenames = [f for f in os.listdir(savepath) if os.path.isfile(os.path.join(savepath, f))]
        return filenames

    def get_filepath_using_public_key(self, public_key) -> str:
        saved_filenames = self.get_saved_filenames()
        for filename in saved_filenames:
            file_public_key = filename[:64]
            if public_key == file_public_key:
                return os.path.join(savepath, filename)

        return ""

    def get_filename_using_private_key(self, private_key) -> str:
        saved_filenames = self.get_saved_filenames()
        for filename in saved_filenames:
            file_public_key = filename[:64]
            file_private_key = self.crypto_handler.calculate_private_key(file_public_key)
            if private_key == file_private_key:
                return filename

        return ""

    def get_original_filename(self, filepath: str) -> str:
        filename = filepath.split("/")[-1][64:]
        return filename

    def delete_saved_file(self, filename: str):
        filepath = os.path.join(savepath, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
