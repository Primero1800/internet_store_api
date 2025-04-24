from typing import TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException

from .exceptions import Errors
from ..user.repository import UsersRepository
from ...auth.dependencies import get_user_manager

if TYPE_CHECKING:
    from src.core.models import (
        User,
    )


class ValidRelationsException(Exception):
    pass


class ValidRelationsInspector:
    def __init__(self, session: AsyncSession, **kwargs):
        self.session = session
        self.need_inspect = []
        self.result = {}
        self.error = None

        if "user_id" in kwargs:
            self.need_inspect.append(("user_id", kwargs["user_id"]))

    async def inspect(self):
        while self.need_inspect:
            to_inspect, params = self.need_inspect.pop(0)
            try:
                if to_inspect == "user_id" and params:
                    await self.expecting_user_exists(user_id=params)
            except ValidRelationsException:
                return self.error
        return self.result

    async def expecting_user_exists(self, user_id: int):
        # Expecting if chosen product exists
        try:
            users_repository: UsersRepository = UsersRepository(
                session=self.session,
            )
            user_orm: "User" = await users_repository.get_one_complex(id=user_id, maximized=False)
            self.result['user_orm'] = user_orm
        except CustomException as exc:
            self.error = ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
            raise ValidRelationsException
