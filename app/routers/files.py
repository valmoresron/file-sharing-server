from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.common import settings
from app.models.responses import FileUploadResponse


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


@router.post("/", response_model=FileUploadResponse)
def upload_file():
    return "test"


@router.delete("/{private_key}")
def delete_file():
    pass


@router.get("/{public_key")
def get_file(public_key: str):
    return JSONResponse({"secret_key": settings.secret_key, "public_key": public_key})
