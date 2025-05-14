import logging
from typing import Union, TYPE_CHECKING

from fastapi import status
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_users import BaseUserManager, models
from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .exceptions import NoSessionException, Errors
from src.core.models import User
from src.tools.exceptions import CustomException

if TYPE_CHECKING:
    from .schemas import (
        UserCreate,
        UserUpdate,
        UserUpdateExtended,
    )

logger = logging.getLogger(__name__)


CLASS = "User"


class UsersRepository:
    def __init__(
        self,
        session: AsyncSession | None = None,
        user_manager: BaseUserManager[models.UP, models.ID] | None = None,
    ):
        self.user_manager = user_manager
        self.session = session
        self.logger = logger

    async def get_one_complex(
            self,
            id: int = None,
            maximized: bool = True,
            relations: list | None = None
    ):
        stmt_filter = select(User).where(User.id == id)

        options_list = []

        if maximized or (relations and "votes" in relations):
            options_list.append(joinedload(User.votes))

        if maximized or (relations and "posts" in relations):
            options_list.append(joinedload(User.posts))

        stmt = stmt_filter.options(*options_list)

        result: Result = await self.session.execute(stmt)
        orm_model: User | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_one_complex_by_email(
            self,
            email: str,
            maximized: bool = True,
            relations: list | None = None
    ):
        stmt_filter = select(User).where(User.email == email)

        options_list = []

        if maximized or (relations and "votes" in relations):
            options_list.append(joinedload(User.votes))

        if maximized or (relations and "posts" in relations):
            options_list.append(joinedload(User.posts))

        stmt = stmt_filter.options(*options_list)

        result: Result = await self.session.execute(stmt)
        orm_model: User | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all_users(
            self,
            filter_model: Filter,
    ):
        if not self.session:
            self.logger.error(
                "Impossible to get all users from database, because no active session. "
                "Raised NoSessionException"
            )
            raise NoSessionException(
                status_code=status.HTTP_400_BAD_REQUEST,
                msg="No active sessions found"
            )

        query_filter = filter_model.filter(select(User))
        stmt = filter_model.sort(query_filter)
        # stmt = query_filter.order_by(User.id)
        result: Result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["UserCreate", "UserUpdate", "UserUpdateExtended"]
    ):
        dict_to_push = instance.model_dump()
        dict_to_push['hashed_password'] = self.user_manager.password_helper.hash(instance.password)
        del dict_to_push['password']
        orm_model: User = User(
            **dict_to_push
        )
        return orm_model

    async def create_one_empty(
            self,
            orm_model: User
    ):
        try:
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%r %r was successfully created" % (CLASS, orm_model))
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                msg=Errors.already_exists_email(orm_model.email)
            )
