import logging
from fastapi import status
from typing import Sequence, TYPE_CHECKING, Union

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import Person
from src.tools.exceptions import CustomException
from .exceptions import Errors

if TYPE_CHECKING:
    from .schemas import (
        PersonCreate,
        PersonUpdate,
        PersonPartialUpdate,
    )
    from .filters import PersonFilter


CLASS = "Person"


class PersonsRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_one_complex(
            self,
            user_id: int = None,
            maximized: bool = True,
            relations: list = [],
    ):
        stmt_filter = select(Person).where(Person.user_id == user_id)

        options_list = []

        if maximized or "user" in relations:
            options_list.append(joinedload(Person.user))

        stmt = stmt_filter.options(*options_list)

        result: Result = await self.session.execute(stmt)
        orm_model: Person | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"user_id={user_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_one(
            self,
            user_id: int
    ):
        orm_model = await self.session.get(Person, user_id)
        if not orm_model:
            text_error = f"user_id={user_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all(
            self,
            filter_model: "PersonFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(Person))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.order_by(Person.user_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_all_full(
            self,
            filter_model: "PersonFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(Person))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
            joinedload(Person.user),
        ).order_by(Person.user_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["PersonCreate", "PersonUpdate", "PersonPartialUpdate"]
    ):
        orm_model: Person = Person(**instance.model_dump())
        return orm_model

    async def create_one_empty(
            self,
            orm_model: Person
    ):
        try:
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%r %r was successfully created" % (CLASS, orm_model))
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                msg=Errors.already_exists_id(orm_model.user_id)
            )

    async def delete_one(
            self,
            orm_model: Person,
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
            instance:  Union["PersonUpdate", "PersonPartialUpdate"],
            orm_model: Person,
            is_partial: bool = False
    ):
        for key, val in instance.model_dump(
                exclude_unset=is_partial,
                exclude_none=is_partial,
        ).items():
            setattr(orm_model, key, val)

        self.logger.warning(f"Editing %r in database" % orm_model)
        try:
            await self.session.commit()
            await self.session.refresh(orm_model)
        except IntegrityError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg=Errors.DATABASE_ERROR()
            )
