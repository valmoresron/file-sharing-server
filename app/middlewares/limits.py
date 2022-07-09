import os

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.common import database, settings
from app.utils import SavedFilesHandler

# this middleware handles limits based on <DAILY_LIMIT_MB> environment variable
# host is the IP of the client accessing the API
class LimitsMiddleware(BaseHTTPMiddleware):
    # access the database and return how much size the host had used for the current date
    def __get_host_used_size(self, host: str):
        db: dict = database.get_db()
        hosts: dict = db["hosts_info"]["hosts"]

        if host not in hosts.keys():
            return 0

        return hosts[host]["used_size"]

    # return how much size the host has remaining
    def __get_host_remaining_size(self, host):
        daily_limit_mb = settings.DAILY_LIMIT_MB
        daily_limit_bytes = daily_limit_mb * 1000 * 1000

        used_size = self.__get_host_used_size(host)
        return daily_limit_bytes - used_size

    # access the database and increment the host's use size
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

        # proceed if accessing /files api using GET and POST method

        host = request.client.host  # client's ip address
        remaining_size = self.__get_host_remaining_size(host)
        remaining_size_mb = remaining_size / (1000 * 1000)

        if request.method == "POST":
            upload_size = int(request.headers.get("content-length"))  # get upload size from request header

            # if upload size is more than the client's remaining daily size, 403 error along with message
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
                # use the saved files handler to determine info about the file the client wants to download
                saved_files_handler = SavedFilesHandler()
                filepath = saved_files_handler.get_filepath_using_public_key(public_key)
                filesize = saved_files_handler.get_file_size(filepath)

                # if file size is more than the client's remaining daily size, 403 error along with message
                if filesize > remaining_size:
                    file_size_mb = filesize / (1000 * 1000)
                    message = f"File size is {round(file_size_mb, 2)} MB. You only have {round(remaining_size_mb, 2)} MB remaining"
                    return JSONResponse({"details": message}, status_code=status.HTTP_403_FORBIDDEN)
                else:
                    self.__increment_host_used_size(host, filesize)

        # if everything works fine, pass along the response to the next middleware or to the route function
        response = await call_next(request)
        return response
