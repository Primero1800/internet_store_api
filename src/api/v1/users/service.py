import logging
from typing import TYPE_CHECKING

from fastapi import status
from fastapi.responses import ORJSONResponse
from fastapi_users import BaseUserManager, models
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import UsersRepository
from .exceptions import NoSessionException

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
                    "message": "Handled by Service exception handler",
                    "detail": exc.msg,
                }
            )
        except IntegrityError as exc:
            self.logger.error("Database error", exc_info=exc)
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "Handled by Service exception handler",
                    "detail": "Internal server error while working with database",
                }
            )
