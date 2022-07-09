from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils import ActivityHandler


# every time the /files subroute is hit, it will update the last activity to the current time
class ActivityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        base_url = str(request.base_url)
        url = str(request.url)
        route = url.replace(base_url, "").split("/")[0]
        if route == "files":
            ActivityHandler.update_last_activity()

        response = await call_next(request)
        return response
