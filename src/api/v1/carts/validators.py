from typing import TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException

from .exceptions import Errors

from ..users.user.repository import UsersRepository
# from ...store.products.repository import ProductsRepository

if TYPE_CHECKING:
    from src.core.models import (
        Product,
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
                if to_inspect == "user_id" and isinstance(params, int):
                    await self.expecting_user_exists(user_id=params)
            except ValidRelationsException:
                return self.error
        return self.result

    async def expecting_user_exists(self, user_id: int):
        # Expecting if chosen user exists
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
