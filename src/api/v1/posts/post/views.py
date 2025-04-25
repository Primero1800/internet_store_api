from typing import TYPE_CHECKING, List, Optional, Dict, Any

from fastapi import (
    APIRouter,
    Form,
    Depends,
    status,
    Request,
    Query,
)
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.scrypts.pagination import paginate_result
from .service import PostService
from .schemas import (
    PostRead,
    PostShort,
)
from .filters import PostFilter
from src.api.v1.users.user.dependencies import current_superuser, current_user
from src.core.config import DBConfigurer, RateLimiter
from ...store.products.schemas import ProductShort
from src.api.v1.users.user.schemas import UserPublicExtended
from . import dependencies as deps

if TYPE_CHECKING:
    from src.core.models import(
        User,
        Vote,
    )


RELATIONS_LIST = [
    {
        "name": "user",
        "usage": "/{id}/user",
        "conditions": "private"
    },
    {
        "name": "product",
        "usage": "/{id}/product",
        "conditions": "public"
    },
]