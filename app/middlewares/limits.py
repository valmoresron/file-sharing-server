import os

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.common import database, settings
from app.utils import SavedFilesHandler


class LimitsHandler(BaseHTTPMiddleware):
    def __get_host_used_size(self, host: str):
        db: dict = database.get_db()
        hosts: dict = db["hosts_info"]["hosts"]

        if host not in hosts.keys():
            return 0

        return hosts[host]["used_size"]

    def __get_host_remaining_size(self, host):
        daily_limit_mb = settings.DAILY_LIMIT_MB
        daily_limit_bytes = daily_limit_mb * 1000 * 1000

        used_size = self.__get_host_used_size(host)
        return daily_limit_bytes - used_size

    def __increment_host_used_size(self, host: str, size: int):
        db: dict = database.get_db()
        hosts: dict = db["hosts_info"]["hosts"]

        if not hosts.get(host):
            hosts[host] = {"used_size": 0}

        hosts[host]["used_size"] += size
        database.set_db(db)

    async def dispatch(self, request: Request, call_next):
        base_url = str(request.base_url)
        url = str(request.url)
        route = url.replace(base_url, "").split("/")[0]
        method = request.method
        if route != "files" or method == "DELETE":
            response = await call_next(request)
            return response

        host = request.client.host
        remaining_size = self.__get_host_remaining_size(host)
        remaining_size_mb = remaining_size / (1000 * 1000)

        if request.method == "POST":
            upload_size = int(request.headers.get("content-length"))
            if upload_size > remaining_size:
                upload_size_mb = upload_size / (1000 * 1000)
                message = f"Upload size is {round(upload_size_mb, 2)} MB. You only have {round(remaining_size_mb, 2)} MB remaining"
                return JSONResponse({"details": message}, status_code=status.HTTP_403_FORBIDDEN)
            else:
                self.__increment_host_used_size(host, upload_size)

        if request.method == "GET":
            public_key = ""
            try:
                public_key = url.replace(base_url, "").split("/")[1]
            except:
                pass

            if public_key:
                saved_files_handler = SavedFilesHandler()
                filepath = saved_files_handler.get_filepath_using_public_key(public_key)
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    file_stat = os.stat(filepath)
                    file_size = file_stat.st_size

                    if file_size > remaining_size:
                        file_size_mb = file_size / (1000 * 1000)
                        message = f"File size is {round(file_size_mb, 2)} MB. You only have {round(remaining_size_mb, 2)} MB remaining"
                        return JSONResponse({"details": message}, status_code=status.HTTP_403_FORBIDDEN)
                    else:
                        self.__increment_host_used_size(host, file_size)

        response = await call_next(request)
        return response
