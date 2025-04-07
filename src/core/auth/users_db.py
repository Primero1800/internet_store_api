from typing import TYPE_CHECKING
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from src.core.config import DBConfigurer
from src.core.models.users.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_db(
        session: "AsyncSession" = Depends(DBConfigurer.session_getter)
):
    yield SQLAlchemyUserDatabase(session, User)