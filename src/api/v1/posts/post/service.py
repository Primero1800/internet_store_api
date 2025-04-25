import logging
from typing import TYPE_CHECKING, Optional

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import PostsRepository
from .schemas import (
    PostCreate,
    PostUpdate,
    PostPartialUpdate,
)
from .exceptions import Errors
from .validators import ValidRelationsInspector


if TYPE_CHECKING:
    from src.core.models import (
        Post,
        User,
    )
    from .filters import PostFilter

CLASS = "Post"
_CLASS = "post"


class PostsService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all(
            self,
            filter_model: "PostFilter",
    ):
        repository: PostsRepository = PostsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "PostFilter"
    ):
        repository: PostsRepository = PostsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all_full(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        return result
