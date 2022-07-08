from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse, Response

from app.utils import FileUploadHandler, SavedFilesHandler
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

    saved_files_handler = SavedFilesHandler()
    filename = saved_files_handler.get_filename_using_private_key(private_key)
    if filename:
        saved_files_handler.delete_saved_file(filename)
        return JSONResponse({"detail": "Delete successful"})

    response.status_code = status.HTTP_404_NOT_FOUND
    return not_found_exception


@router.get("/{public_key}")
def get_file(public_key: str, response: Response):
    if len(public_key) != 64:
        response.status_code = status.HTTP_404_NOT_FOUND
        return not_found_exception

    saved_files_handler = SavedFilesHandler()
    filepath = saved_files_handler.get_filepath_using_public_key(public_key)
    if filepath:
        filename = saved_files_handler.get_original_filename(filepath)
        return FileResponse(filepath, filename=filename)

    response.status_code = status.HTTP_404_NOT_FOUND
    return not_found_exception
