import logging
from typing import TYPE_CHECKING, Any, Union

from fastapi import status, Request
from fastapi.responses import ORJSONResponse
from fastapi_users import BaseUserManager, models, exceptions
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.settings import settings
from src.tools.exceptions import CustomException
from . import utils
from .repository import UsersRepository
from .exceptions import NoSessionException, Errors
from src.api.v1.auth.exceptions import Errors as Auth_Errors
from .schemas import UserCreate


if TYPE_CHECKING:
    from .filters import UserFilter
    from src.core.models import User


class UsersService:
    def __init__(
        self,
        user_manager: BaseUserManager[models.UP, models.ID],
        session: AsyncSession | None = None
    ):
        self.user_manager = user_manager
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all_users(
            self,
            filter_model: "UserFilter"
    ):

        repository: UsersRepository = UsersRepository(
            session=self.session,
        )
        try:
            result = await repository.get_all_users(
                filter_model=filter_model
            )
            return result
        except NoSessionException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
        except IntegrityError as exc:
            self.logger.error("Database error", exc_info=exc)
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": Errors.DATABASE_ERROR(),
                }
            )

    async def update_me(
            self,
            request: Request,
            user_update: Any,
            user: models.UP,
    ):
        try:
            user = await self.user_manager.update(
                user_update, user, safe=True, request=request
            )
            return user

        except exceptions.InvalidPasswordException as e:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": Auth_Errors.invalid_password_reasoned(e.reason),
                }
            )

        except exceptions.UserAlreadyExists:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": Auth_Errors.user_already_exists_emailed(user_update.email),
                }
            )

    async def get_one_complex(
            self,
            id: int,
            maximized: bool = True,
            relations: list | None = None,
            to_schema: bool = True,
    ):
        repository: UsersRepository = UsersRepository(
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
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
        if to_schema:
            return await utils.get_schema_from_orm(
                returned_orm_model,
                maximized=maximized,
                relations=relations
            )
        return returned_orm_model

    async def create_default_superuser(
            self,
            email: str | None = None,
            password: str | None = None,
            to_schema: bool = True,
            return_none: bool = True,
    ):
        email = email or settings.users.SUPERUSER_DEFAULT_EMAIL
        password = password or settings.users.SUPERUSER_DEFAULT_PASSWORD

        repository: UsersRepository = UsersRepository(
            session=self.session,
            user_manager=self.user_manager
        )

        orm_model: Union["User", None] = None
        self.logger.warning("Inspecting if default superuser exists")
        try:
            orm_model = await repository.get_one_complex_by_email(
                email=email
            )
            self.logger.info("Default superuser already exists")
        except CustomException:
            self.logger.warning("Found no default superuser in current db. Creating new one")

        if not orm_model:

            # Expecting if ProductCreate data valid
            # catching ValidationError in exception_handler
            instance: UserCreate = UserCreate(
                firstname=None,
                lastname=None,
                email=email,
                password=password,
                is_active=True,
                is_superuser=True,
                is_verified=True,
            )

            orm_model = await repository.get_orm_model_from_schema(instance=instance)
            try:
                await repository.create_one_empty(
                    orm_model=orm_model,
                )
                self.logger.info("Default superuser was successfully created")
            except CustomException as exc:
                self.logger.error('Error occurred while creating default superuser')
                return ORJSONResponse(
                    status_code=exc.status_code,
                    content={
                        "message": Errors.HANDLER_MESSAGE(),
                        "detail": exc.msg,
                    }
                )

        if return_none:
            return

        return await self.get_one_complex(
            id=orm_model.id,
            to_schema=to_schema
        )
