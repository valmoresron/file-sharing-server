from pydantic import BaseModel

class FileUploadResponse(BaseModel):
    privateKey: str
    publicKey: str