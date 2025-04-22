import logging
from typing import Sequence, TYPE_CHECKING, Union

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import Vote, Product, ProductImage, User
from src.tools.exceptions import CustomException
from .exceptions import Errors

if TYPE_CHECKING:
    from .schemas import (
        VoteCreate,
        VoteUpdate,
        VotePartialUpdate,
    )
    from .filters import VoteFilter


CLASS = "Vote"


class VotesRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_one_complex(
            self,
            id: int = None,
            maximized: bool = True,
            relations: list = []
    ):
        stmt_filter = select(Vote).where(Vote.id == id)

        options_list = [
        ]

        if maximized or "product" in relations:
            options_list.append(joinedload(Vote.product).joinedload(Product.images))

        if maximized or "user" in relations:
            options_list.append(joinedload(Vote.user))

        stmt = stmt_filter.options(*options_list)

        result: Result = await self.session.execute(stmt)
        orm_model: Vote | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_one(
            self,
            id: int
    ):
        orm_model = await self.session.get(Vote, id)
        if not orm_model:
            text_error = f"id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all(
            self,
            filter_model: "VoteFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(Vote))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.order_by(Vote.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_all_full(
            self,
            filter_model: "VoteFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(Vote))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
            joinedload(Vote.product).joinedload(Product.images),
            joinedload(Vote.user),
        ).order_by(Vote.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["VoteCreate", "VoteUpdate", "VotePartialUpdate"]
    ):
        orm_model: Vote = Vote(**instance.model_dump())
        return orm_model

    async def create_one_empty(
            self,
            orm_model: Vote
    ):
        try:
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%r %r was successfully created" % (CLASS, orm_model))
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                msg=Errors.already_exists_titled(orm_model.user_id, orm_model.product_id)
            )
