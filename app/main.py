from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.settings import Settings

app = FastAPI()
settings = Settings()


@app.get("/")
def home():
    docs_url = "/docs"
    return RedirectResponse(url=docs_url)


@app.post("/file")
def upload_file():
    pass


@app.delete("/file/{private_key}")
def delete_file():
    pass


@app.get("/file/{public_key}")
def get_file():
    return settings.secret_key
