import os, hashlib, hmac, time, pathlib

from fastapi import UploadFile
from app.common import settings

secret_key = settings.SECRET_KEY
savepath = str(settings.FOLDER)

# if the specified folder does not exist, this will automatically create it
os.makedirs(savepath, exist_ok=True)

# handles the calculation of the public and private keys
class CryptoHandler:
    # use the contents of the file as bytes to calculate a public key;
    # the public key is simply a hash of the file
    def calculate_public_key(self, contents: bytes) -> str:
        hash = hashlib.sha256(contents)
        public_key = hash.hexdigest()
        return public_key

    # use a message, in this case a public key, to calculate a private key
    # it will also use the SECRET_KEY environment variable to encrypt the public key
    def calculate_private_key(self, message: str) -> str:
        digestmod = "sha256"
        private_key = hmac.new(
            key=secret_key.encode(),
            msg=message.encode(),
            digestmod=digestmod,
        ).hexdigest()
        return private_key


# handles uploaded file
class FileUploadHandler:
    file: UploadFile
    file_contents: bytes
    public_key: str
    private_key: str
    crypto_handler: CryptoHandler

    # the constructor receives the uploaded file; initialize class properties; calculate public and private keys
    def __init__(self, file: UploadFile):
        self.file = file
        self.file_contents = file.file.read()  # read the contents of the file
        self.private_key = ""
        self.public_key = ""
        self.crypto_handler = CryptoHandler()  # handles the calculation of the public and private keys
        self.__calculate_public_key()  # calculate public key and assign it to the public_key property
        self.__calculate_private_key()  # calculate the private key and assign it to the private_key property

    # uses the contents of the file to product the public key
    def __calculate_public_key(self):
        if not self.public_key:
            file_contents = self.file_contents
            public_key = self.crypto_handler.calculate_public_key(file_contents)
            self.public_key = public_key

    # uses the public key to calculate the private key; crypto handler also uses the SECRET_KEY variable for calculation
    def __calculate_private_key(self):
        if not self.private_key:
            self.__calculate_public_key()
            public_key = self.public_key
            private_key = self.crypto_handler.calculate_private_key(public_key)
            self.private_key = private_key

    # saves the file with a filename prepended with the public key
    def save_file(self):
        uploaded_filename = self.file.filename
        save_filename = self.public_key + uploaded_filename
        save_filepath = os.path.join(savepath, save_filename)

        with open(save_filepath, "wb") as f:
            f.write(self.file_contents)


# handles the saved files
class SavedFilesHandler:
    crypto_handler: CryptoHandler  # use the crypto handler to calculate public and private keys

    def __init__(self) -> None:
        self.crypto_handler = CryptoHandler()  # initialize the cryto handler

    # returns the list of all the files inside the folder specified in the FOLDER environment variable
    def get_saved_filenames(self) -> list[str]:
        filenames = [f for f in os.listdir(savepath) if os.path.isfile(os.path.join(savepath, f))]
        return filenames

    # returns the path to the file referred using the public key; if no file is found, return an empty string
    def get_filepath_using_public_key(self, public_key) -> str:
        saved_filenames = self.get_saved_filenames()
        for filename in saved_filenames:
            file_public_key = filename[:64]
            if public_key == file_public_key:
                return os.path.join(savepath, filename)

        return ""

    # get the name of the file using the private key; if nothing matches, return an empty string
    def get_filename_using_private_key(self, private_key) -> str:
        saved_filenames = self.get_saved_filenames()
        for filename in saved_filenames:  # loop through all the filenames
            file_public_key = filename[:64]  # the first 64 characters is the public key

            # use the crypto handler to calculate the private key using the public key;
            # if the private key matches, return the name of the file
            file_private_key = self.crypto_handler.calculate_private_key(file_public_key)
            if private_key == file_private_key:
                return filename

        return ""

    # names of the saved files are (public key + original filename)
    # public keys are 64 characters long, so to get the original filename, cut of the first 64 characters
    def get_original_filename(self, filepath: str) -> str:
        filename = pathlib.Path(filepath).name[64:]
        return filename

    # delete saved file using the filename
    def delete_saved_file(self, filename: str):
        filepath = os.path.join(savepath, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    # get the file's size using a filepath; if the file does not exist, return 0
    def get_file_size(self, filepath) -> int:
        if os.path.exists(filepath) and os.path.isfile(filepath):
            file_stat = os.stat(filepath)
            file_size = file_stat.st_size
            return file_size

        return 0

    # removes all the files specified in the FOLDER environment variable
    def clean_up_files(self):
        filenames = self.get_saved_filenames()
        for filename in filenames:  # loop through all the filenames and delete each file
            self.delete_saved_file(filename)


# a global variable to store time of the last activity
LAST_ACTIVITY: float = time.time()

# this handles settings, getting and calculating time of last activity
class ActivityHandler:
    # simply returns the value of the last activity
    @staticmethod
    def get_last_activity() -> float:
        global LAST_ACTIVITY
        return LAST_ACTIVITY

    # update the value of last activity to the current time
    @staticmethod
    def update_last_activity():
        global LAST_ACTIVITY
        LAST_ACTIVITY = time.time()

    # calculate the time in minutes from the last activity
    @staticmethod
    def get_mins_from_last_activity() -> int:
        global LAST_ACTIVITY
        current_time = time.time()
        time_diff = current_time - LAST_ACTIVITY
        time_diff_mins = time_diff / 60
        return int(time_diff_mins)
