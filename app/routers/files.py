from fastapi import APIRouter
from app.common import settings


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
def get_file(public_key: str):
    return {"secret_key": settings.secret_key, "public_key": public_key}
