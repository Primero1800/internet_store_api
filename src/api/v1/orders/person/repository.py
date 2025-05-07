import logging
from fastapi import status
from typing import Sequence, TYPE_CHECKING, Union, Optional, Any

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import Person, User
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
