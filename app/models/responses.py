from pydantic import BaseModel

# the response model to return when the client uploads a file
class FileUploadResponse(BaseModel):
    privateKey: str
    publicKey: str
