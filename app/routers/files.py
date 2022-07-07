from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from app.utils import FileUploadHandler, get_saved_filenames, get_saved_filepath
from app.models.responses import FileUploadResponse


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)

not_found_exception = HTTPException(status_code=404, detail="File not found")


@router.post("/", response_model=FileUploadResponse)
def upload_file(file: UploadFile):
    handler = FileUploadHandler(file)
    handler.save_file()
    return JSONResponse({"publicKey": handler.public_key, "privateKey": handler.private_key})


@router.delete("/{private_key}")
def delete_file():
    pass


@router.get("/{public_key}")
def get_file(public_key: str):
    if len(public_key) != 64:
        return not_found_exception

    saved_filenames = get_saved_filenames()
    for filename in saved_filenames:
        if filename.startswith(public_key):
            saved_filepath = get_saved_filepath(filename)
            original_filename = filename.replace(public_key, "")
            print(original_filename)
            return FileResponse(saved_filepath, filename=original_filename)

    return not_found_exception
