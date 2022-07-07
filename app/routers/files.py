from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse, Response

from app.utils import FileUploadHandler, CryptoHandler, get_saved_filenames, get_saved_filepath, delete_saved_file
from app.models.responses import FileUploadResponse


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)

not_found_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")


@router.post("/", response_model=FileUploadResponse)
def upload_file(file: UploadFile):
    file_upload_handler = FileUploadHandler(file)
    file_upload_handler.save_file()
    return JSONResponse({"publicKey": file_upload_handler.public_key, "privateKey": file_upload_handler.private_key})


@router.delete("/{private_key}")
def delete_file(private_key: str, response: Response):
    if len(private_key) != 64:
        response.status_code = status.HTTP_404_NOT_FOUND
        return not_found_exception

    crypto_handler = CryptoHandler()
    saved_filenames = get_saved_filenames()
    for filename in saved_filenames:
        public_key = filename[:64]
        file_private_key = crypto_handler.calculate_private_key(public_key)
        if file_private_key == private_key:
            delete_saved_file(filename)
            return JSONResponse({"detail": "Delete successful"})

    response.status_code = status.HTTP_404_NOT_FOUND
    return not_found_exception


@router.get("/{public_key}")
def get_file(public_key: str, response: Response):
    if len(public_key) != 64:
        response.status_code = status.HTTP_404_NOT_FOUND
        return not_found_exception

    saved_filenames = get_saved_filenames()
    for filename in saved_filenames:
        if filename.startswith(public_key):
            saved_filepath = get_saved_filepath(filename)
            original_filename = filename.replace(public_key, "")
            return FileResponse(saved_filepath, filename=original_filename)

    response.status_code = status.HTTP_404_NOT_FOUND
    return not_found_exception
