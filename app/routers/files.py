from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse, Response

from app.utils import FileUploadHandler, SavedFilesHandler
from app.models.responses import FileUploadResponse

# tags is useful for swagger documentation; to group routes together
router = APIRouter(prefix="/files", tags=["Files"])

# exception to be returned if the file is not found
not_found_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

# this route handles the file upload
@router.post("/", response_model=FileUploadResponse)
def upload_file(file: UploadFile):
    # when a file is uploaded, pass it to the file upload handler to handle uploaded file
    file_upload_handler = FileUploadHandler(file)
    file_upload_handler.save_file()  # this will save the file

    # return a response along with the public and private keys
    return JSONResponse({"publicKey": file_upload_handler.public_key, "privateKey": file_upload_handler.private_key})


# this route handles the file deletion; accepts a url parameter called private_key
@router.delete("/{private_key}")
def delete_file(private_key: str, response: Response):
    # the private key will always be 64 characters long; if not automatically return 404 not found error
    if len(private_key) != 64:
        response.status_code = status.HTTP_404_NOT_FOUND
        return not_found_exception

    # use the saved files handler to get the filename using the private key
    saved_files_handler = SavedFilesHandler()
    filename = saved_files_handler.get_filename_using_private_key(private_key)

    # if a filename is found use the handler to delete the file and return a sucess status
    if filename:
        saved_files_handler.delete_saved_file(filename)
        return JSONResponse({"detail": "Delete successful"})

    # if filename does not exist, return a not found error
    response.status_code = status.HTTP_404_NOT_FOUND
    return not_found_exception


# this route handles file download
@router.get("/{public_key}")
def get_file(public_key: str, response: Response):
    # the public key will always be 64 characters long; if not automatically return 404 not found error
    if len(public_key) != 64:
        response.status_code = status.HTTP_404_NOT_FOUND
        return not_found_exception

    # use the saved files handler to get the filepath using the public key
    saved_files_handler = SavedFilesHandler()
    filepath = saved_files_handler.get_filepath_using_public_key(public_key)

    # if a filepath exists, use the handler to get the original filename when the file was uploaded and return it
    if filepath:
        filename = saved_files_handler.get_original_filename(filepath)
        return FileResponse(filepath, filename=filename)  # returns the file along with the original filename

    # # if filepath does not exist, return a not found error
    response.status_code = status.HTTP_404_NOT_FOUND
    return not_found_exception
