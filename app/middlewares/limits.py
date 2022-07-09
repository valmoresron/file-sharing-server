from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.common import database


class LimitsHandler(BaseHTTPMiddleware):
    def get_host_used_size(self):
        pass

    def get_host_remaining_size(self):
        pass

    async def dispatch(self, request: Request, call_next):
        base_url = str(request.base_url)
        url = str(request.url)
        route = url.replace(base_url, "").split("/")[0]
        method = request.method
        if route != "files" or method == "DELETE":
            response = await call_next(request)
            return response

        host = request.client.host
        if request.method == "POST":
            upload_size = int(request.headers.get("content-length"))
            return JSONResponse({"details": "Reached daily limit"}, status_code=status.HTTP_403_FORBIDDEN)
