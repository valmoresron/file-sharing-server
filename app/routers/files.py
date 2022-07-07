from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse

from app.common import settings
from app.models.responses import FileUploadResponse
from app.utils import FileUploadHandler


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


@router.post("/", response_model=FileUploadResponse)
def upload_file(file: UploadFile):
    handler = FileUploadHandler(file)
    handler.save_file()
    return JSONResponse({"publicKey": handler.public_key, "privateKey": handler.private_key})


@router.delete("/{private_key}")
def delete_file():
    pass


@router.get("/{public_key")
def get_file(public_key: str):
    return JSONResponse({"secret_key": settings.secret_key, "public_key": public_key})
