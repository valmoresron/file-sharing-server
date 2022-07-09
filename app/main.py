from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi_utils.tasks import repeat_every
from app.middlewares.limits import LimitsMiddleware

from app.routers import files
from app.utils import ActivityHandler, SavedFilesHandler
from app.middlewares import ActivityMiddleware
from app.common import settings

app = FastAPI()


# the root url redirects to /docs for some swagger ui
@app.get("/", tags=["Defaults"], description="Redirects to docs")
def home():
    docs_url = "/docs"
    return RedirectResponse(url=docs_url)


# add middlewares
app.add_middleware(ActivityMiddleware)  # middleware used for updating last activity
app.add_middleware(LimitsMiddleware)  # middleware for validating daily upload/download limit

# add subroutes
app.include_router(files.router)  # subrouting for /files API


# check every 10 secs if cleanup can proceed;
# if last activity was more than the time specified in the CLEANUP_AFTER_MINS_INACTIVITY environment variable, cleanup will proceed
@app.on_event("startup")
@repeat_every(seconds=10)
def clean_up():
    last_activity_mins = ActivityHandler.get_mins_from_last_activity()
    if last_activity_mins >= settings.CLEANUP_AFTER_MINS_INACTIVITY:
        ActivityHandler.update_last_activity()
        saved_files_handler = SavedFilesHandler()
        saved_files_handler.clean_up_files()
