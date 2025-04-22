import logging
from typing import TYPE_CHECKING, Optional

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
from .validators import ValidRelationsInspector

if TYPE_CHECKING:
    from src.core.models import (
        Vote,
        User,
    )
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

    async def get_all_full(
            self,
            filter_model: "VoteFilter"
    ):
        repository: VotesRepository = VotesRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all_full(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        return result

    async def get_one(
            self,
            id: int,
            to_schema: bool = True
    ):
        repository: VotesRepository = VotesRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one(
                id=id,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        if to_schema:
            await utils.get_short_schema_from_orm(returned_orm_model)
        return returned_orm_model

    async def get_one_complex(
            self,
            id: int = None,
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        repository: VotesRepository = VotesRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one_complex(
                id=id,
                maximized=maximized,
                relations=relations,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        if to_schema:
            if not maximized and not relations:
                return await utils.get_short_schema_from_orm(
                    returned_orm_model
                )
            return await utils.get_schema_from_orm(
                returned_orm_model,
                maximized=maximized,
                relations=relations,
            )
        return returned_orm_model

    async def create_one(
            self,
            user: "User",
            product_id: int,
            name: str,
            stars: int,
            review: Optional[str] = None,
    ):
        repository: VotesRepository = VotesRepository(
            session=self.session
        )

        # catching ValidationError in exception_handler
        instance: VoteCreate = VoteCreate(
            user_id=user.id,
            product_id=product_id,
            name=name,
            review=review,
            stars=stars,
        )
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

        inspector = ValidRelationsInspector(
            session=self.session,
            **{"product_id": product_id}
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result
        # product_orm = result["product_orm"] if "product_orm" in result else None

        try:
            await repository.create_one_empty(orm_model=orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

        self.logger.info("Brand %r was successfully created" % orm_model)

        return await self.get_one_complex(
            id=orm_model.id
        )
