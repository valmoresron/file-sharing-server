from dotenv import load_dotenv
from pydantic import BaseSettings
from pathlib import Path

# loads all the environment variables inside the .env file
load_dotenv()


# This class contains all the settings for the app
# it inherits from pydantic.BaseSettings to automatically validate its values based on the type
# by default, all the properties inside this class will automatically assigned with the corresponding environment variable
class Settings(BaseSettings):
    SECRET_KEY: str  # key used for calculating the private key
    FOLDER: Path  # directory where the uploaded files are saved
    HOST: str  # host used for the server. ex: localhost, 127.0.0.1, 0.0.0.0, etc...
    PORT: int  # port used for the server
    DAILY_LIMIT_MB: int  # upload and download limit for the client with the same IP address
    CLEANUP_AFTER_MINS_INACTIVITY: int  # value in minutes of inactivity; used to determine if clean up will be ran
