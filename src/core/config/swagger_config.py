from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.openapi.docs import (
    get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
)
from starlette import status

from src.core.settings import settings


# /**/**/4_el/src
BASE_DIR: str = str(Path(__file__).resolve().parent.parent.parent.parent)


class SwaggerConfigurer:

    @staticmethod
    async def get_routes(application: FastAPI, path=True, tags=True, methods=True, ):
        routes_info = []
        for route in application.routes:
            route_dict = {}
            if path:
                route_dict['path'] = route.path
            if tags:
                route_dict['tags'] = route.tags if hasattr(route, "tags") else []
            if methods:
                route_dict['methods'] = route.methods
            routes_info.append(route_dict)
        return routes_info

    @staticmethod
    def delete_router_tag(application: FastAPI):
        for route in application.routes:
            if hasattr(route, "tags"):
                if isinstance(route.tags, list) and len(route.tags) > 1:
                    del route.tags[0]

    @staticmethod
    def config_swagger(app: FastAPI, app_title='Unknown application'):

        from src.core.config import RateLimiter

        @app.get(
            '/docs',
            status_code=status.HTTP_200_OK,
            tags=[settings.tags.SWAGGER_TAG],
        )
        @RateLimiter.rate_limit()
        async def custom_swagger_ui_html(
                request: Request,
        ):
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=app_title + ' Swagger UI',
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                # swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
                swagger_js_url=f"/static/swagger/js/swagger-ui-bundle.js",
                # swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
                swagger_css_url=f"/static/swagger/css/swagger-ui.css"
            )

        @app.get(
            app.swagger_ui_oauth2_redirect_url,
            include_in_schema=False
        )
        @RateLimiter.rate_limit()
        async def swagger_ui_redirect(
                request: Request
        ):
            return get_swagger_ui_oauth2_redirect_html()

        @app.get(
            "/redoc",
            status_code=status.HTTP_200_OK,
            tags=[settings.tags.SWAGGER_TAG]
        )
        @RateLimiter.rate_limit()
        async def redoc_html(
                request: Request
        ):
            return get_redoc_html(
                openapi_url=app.openapi_url,
                title=app.title + " - ReDoc",
                # redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
                redoc_js_url=f"/static/swagger/js/redoc.standalone.js"
            )
