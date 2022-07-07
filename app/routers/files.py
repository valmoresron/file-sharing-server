from fastapi import APIRouter
from app.settings import Settings

settings = Settings()

router = APIRouter(
    prefix="/file",
    tags=["file"],
)


@router.post("/")
def upload_file():
    pass


@router.delete("/{private_key}")
def delete_file():
    pass


@router.get("/{public_key}")
def get_file():
    return settings.secret_key
