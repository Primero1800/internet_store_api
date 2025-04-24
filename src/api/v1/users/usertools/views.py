from typing import Dict, Any

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi_filter import FilterDepends
from fastapi_users import BaseUserManager, models, schemas
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.users.user.dependencies import (
    current_superuser,
    current_user,
)
from src.api.v1.users.user.schemas import (
    UserRead,
)
from src.core.config import DBConfigurer, RateLimiter
from src.scrypts.pagination import paginate_result

# from .service import UserToolsService
# from .filters import UserToolsFilter
#
#
# from .schemas import (
#     VoteShort,
# )



router = APIRouter()


RELATIONS_LIST = [
    {
        "name": "user",
        "usage": "/me/user",
        "conditions": "public"
    },
    {
        "name": "user",
        "usage": "/{id}/user",
        "conditions": "private"
    },
]


# 1
@router.get(
    "/routes",
    status_code=status.HTTP_200_OK,
    description="Getting all the routes of the current branch",
)
@RateLimiter.rate_limit()
async def get_routes(
        request: Request,
) -> list[Dict[str, Any]]:
    from src.scrypts.get_routes import get_routes as scrypt_get_routes
    return await scrypt_get_routes(
        application=router,
        tags=False,
        desc=True
    )


# 2
@router.get(
    "/relations",
    status_code=status.HTTP_200_OK,
    description="Getting the relations info for the branch items"
)
@RateLimiter.rate_limit()
async def get_relations(
        request: Request,
) -> list[Dict[str, Any]]:
    return RELATIONS_LIST
