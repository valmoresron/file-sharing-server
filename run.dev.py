import uvicorn

from app.common import settings

if __name__ == "__main__":
    # this runs the development server only if this file is being run and not imported
    uvicorn.run(
        "app:app",
        host=settings.HOST,  # use the host specified in the environment variable
        port=settings.PORT,  # use the port specified in the environment variable
        reload=True,  # reload if changes in the app files are detected
        debug=True,  # show all the debug logs
    )
