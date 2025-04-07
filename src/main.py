from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.core.settings import settings
from src.core.config import AppConfigurer


@asynccontextmanager
async def lifespan(application: FastAPI):
    # startup
    yield
    # shutdown
    # await DBConfigurer.dispose() TODO


app = AppConfigurer.create_app(
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.openapi = AppConfigurer.get_custom_openapi(app)


# ROUTES

@app.get("/", tags=[settings.tags.ROOT_TAG,],)
@app.get("", tags=[settings.tags.ROOT_TAG,], include_in_schema=False,)
def top():
    return f"top here"


@app.get("/echo/{thing}/", tags=[settings.tags.TECH_TAG,],)
@app.get("/echo/{thing}", tags=[settings.tags.TECH_TAG,], include_in_schema=False,)
def echo(thing):
    return " ".join([thing for _ in range(3)])


# @app.get("/routes/", tags=[settings.tags.TECH_TAG,],)
# @app.get("/routes",  tags=[settings.tags.TECH_TAG,], include_in_schema=False,)
# async def get_routes_endpoint():
#     return await SwaggerConfigurer.get_routes(
#         application=app,
#     )


if __name__ == "__main__":
    # gunicorn app1.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    # uvicorn app1.main:app --host 0.0.0.0 --reload
    uvicorn.run(
        app=settings.run.app1.APP_PATH,
        host=settings.run.app1.APP_HOST,
        port=8080,                                 # original 8000 used in uvicorn server, started from system bash
        reload=settings.run.app1.APP_RELOAD,
    )