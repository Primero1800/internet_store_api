from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Depends
from starlette.staticfiles import StaticFiles

from src.api.v1.users.dependencies import current_superuser
from src.core.settings import settings
from src.core.config import (
    AppConfigurer,
    SwaggerConfigurer,
    DBConfigurer,
    RateLimiter,
    ExceptionHandlerConfigurer,
)
from src.api import router as router_api


@asynccontextmanager
async def lifespan(application: FastAPI):
    # startup
    yield
    # shutdown
    await DBConfigurer.dispose()


app = AppConfigurer.create_app(
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)
app.webhooks = []

app.mount("/static", StaticFiles(directory="static"), name="static")

app.openapi = AppConfigurer.get_custom_openapi(app)

# ROUTERS

app.include_router(
    router_api,
    prefix=settings.app.API_PREFIX,
)

SwaggerConfigurer.config_swagger(app, settings.app.APP_TITLE)


# uncomment, if need custom exception_handler
ExceptionHandlerConfigurer.config_exception_handler(app)



######################################################################

SwaggerConfigurer.delete_router_tag(app)


# ROUTES


@app.get(
    "/",
    tags=[settings.tags.ROOT_TAG,],
)
@RateLimiter.rate_limit()
async def top(request: Request):
    return f"top here"


@app.get(
    "/echo/{thing}",
    tags=[settings.tags.TECH_TAG,],
)
@RateLimiter.rate_limit()
def echo(request: Request, thing: str):
    return " ".join([thing for _ in range(3)])


@app.get(
    "/routes",
    tags=[settings.tags.TECH_TAG,],
    dependencies=[Depends(current_superuser)]
)
# no rate limit for superuser
async def get_routes_endpoint(request: Request):
    return await SwaggerConfigurer.get_routes(
        application=app,
    )


if __name__ == "__main__":
    # gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    # uvicorn src.main:app --host 0.0.0.0 --reload
    uvicorn.run(
        app=settings.run.app1.APP_PATH,
        host=settings.run.app1.APP_HOST,
        port=8080,                                 # original 8000 used in uvicorn server, started from system bash
        reload=settings.run.app1.APP_RELOAD,
    )