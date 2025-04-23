import logging
from typing import Sequence, TYPE_CHECKING, Union

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import Vote, Product
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

    async def delete_one(
            self,
            orm_model: Vote,
    ) -> None:
        try:
            self.logger.info(f"Deleting %r from database" % orm_model)
            await self.session.delete(orm_model)
            await self.session.commit()
        except IntegrityError as exc:
            self.logger.error("Error while deleting data from database", exc_info=exc)
            raise CustomException(
                msg="Error while deleting %r from database" % orm_model
            )

    async def edit_one_empty(
            self,
            instance:  Union["VoteUpdate", "VotePartialUpdate"],
            orm_model: Vote,
            is_partial: bool = False
    ):
        for key, val in instance.model_dump(
                exclude_unset=is_partial,
                exclude_none=is_partial,
        ).items():
            setattr(orm_model, key, val)
        product_id = orm_model.product_id
        user_id = orm_model.user_id

        self.logger.warning(f"Editing %r in database" % orm_model)
        try:
            await self.session.commit()
            await self.session.refresh(orm_model)
        except IntegrityError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                msg=Errors.already_exists_titled(user_id, product_id)
            )
