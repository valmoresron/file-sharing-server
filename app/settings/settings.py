from dotenv import load_dotenv
from pydantic import BaseSettings
from pathlib import Path

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str
    FOLDER: Path
    HOST: str
    PORT: int
    CLEANUP_AFTER_MINS: int
