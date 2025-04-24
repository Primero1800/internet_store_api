import logging
from typing import TYPE_CHECKING, Any

from fastapi import status, Request
from fastapi.responses import ORJSONResponse
from fastapi_users import BaseUserManager, models, exceptions
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import UsersRepository
from .exceptions import NoSessionException, Errors
from src.api.v1.auth.exceptions import Errors as Auth_Errors

if TYPE_CHECKING:
    from .filters import UserFilter


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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        except IntegrityError as exc:
            self.logger.error("Database error", exc_info=exc)
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.DATABASE_ERROR,
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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Auth_Errors.invalid_password_reasoned(e.reason),
                }
            )

        except exceptions.UserAlreadyExists:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Auth_Errors.user_already_exists_emailed(user_update.email),
                }
            )

    async def get_one_complex(
            self,
            id: int,
            maximized: bool = True,
            relations: list | None = [],
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
                    "message": Errors.HANDLER_MESSAGE,
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
