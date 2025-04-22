import logging
from typing import TYPE_CHECKING

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import VotesRepository
from .schemas import (
    VoteCreate,
    VoteUpdate,
    VotePartialUpdate,
)
from .exceptions import Errors


if TYPE_CHECKING:
    from src.core.models import Vote
    from .filters import VoteFilter

CLASS = "Vote"
_CLASS = "vote"


class VotesService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all(
            self,
            filter_model: "VoteFilter",
    ):
        repository: VotesRepository = VotesRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

