from typing import TYPE_CHECKING, List, Optional, Dict, Any

from fastapi import (
    APIRouter,
    UploadFile,
    Form,
    File,
    Depends,
    status,
    Request,
    Query,
)
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.scrypts.pagination import paginate_result
from .service import VotesService
from .schemas import (
    VoteRead,
)
from .filters import VoteFilter
from src.api.v1.users.dependencies import current_superuser
from src.core.config import DBConfigurer, RateLimiter
from . import dependencies as deps
from ..products.schemas import ProductShort
from ...users.schemas import UserRead


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


router = APIRouter()