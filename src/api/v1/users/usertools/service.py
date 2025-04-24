import logging
from typing import TYPE_CHECKING, Optional

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from .repository import UserToolsRepository
# from .exceptions import Errors
# from .validators import ValidRelationsInspector
from .schemas import (
    UserToolsCreate,
    UserToolsUpdate,
)
from . import utils

if TYPE_CHECKING:
    from .filters import UserToolsFilter
    from src.core.models import (
        UserTools,
    )

CLASS = "UserTools"
_CLASS = "user_tools"


class UserToolsService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.repository = None

    async def get_all(
            self,
            filter_model: "UserToolsFilter",
    ):
        repository: UserToolsRepository = UserToolsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result
