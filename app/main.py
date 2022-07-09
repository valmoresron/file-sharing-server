from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi_utils.tasks import repeat_every
from app.middlewares.limits import LimitsHandler

from app.routers import files
from app.utils import ActivityHandler, SavedFilesHandler
from app.middlewares import ActivityMiddleware
from app.common import settings

app = FastAPI()


@app.get("/", tags=["Defaults"], description="Redirects to docs")
def home():
    docs_url = "/docs"
    return RedirectResponse(url=docs_url)


app.add_middleware(ActivityMiddleware)
app.add_middleware(LimitsHandler)

app.include_router(files.router)


@app.on_event("startup")
@repeat_every(seconds=10)
def clean_up():
    last_activity_mins = ActivityHandler.get_mins_from_last_activity()
    if last_activity_mins >= settings.CLEANUP_AFTER_MINS_INACTIVITY:
        ActivityHandler.update_last_activity()
        saved_files_handler = SavedFilesHandler()
        saved_files_handler.clean_up_files()
