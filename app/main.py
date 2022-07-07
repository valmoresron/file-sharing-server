from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.settings import Settings
from app.routers import files

app = FastAPI()


@app.get("/", tags=["Defaults"], description="Redirects to docs")
def home():
    docs_url = "/docs"
    return RedirectResponse(url=docs_url)


app.include_router(files.router)
