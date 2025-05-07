from typing import Union, TYPE_CHECKING

from fastapi import Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.orders.person.service import PersonsService
from src.api.v1.users.user.dependencies import user_cookie_or_error
from src.core.config import DBConfigurer

if TYPE_CHECKING:
    from src.core.models import (
        Person,
        User,
    )
    from src.core.sessions.fastapi_sessions_config import SessionData
    from src.api.v1.orders.person.session_person import SessionPerson


async def get_one_session(
        obj_type: Union["User", "SessionData", ORJSONResponse] = Depends(user_cookie_or_error),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> Union["Person", "SessionPerson"]:
    service: PersonsService = PersonsService(
        session=session
    )
    return await service.get_one(
        obj_type=obj_type,
        to_schema=False,
    )


async def get_one_session_full(
        obj_type: Union["User", "SessionData", ORJSONResponse] = Depends(user_cookie_or_error),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> Union["Person", "SessionPerson"]:
    service: PersonsService = PersonsService(
        session=session
    )
    return await service.get_one_complex(
        obj_type=obj_type,
        to_schema=False,
    )


async def get_one_simple(
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "Person":
    service: PersonsService = PersonsService(
        session=session
    )
    return await service.get_one(
        user_id=user_id,
        to_schema=False,
    )
