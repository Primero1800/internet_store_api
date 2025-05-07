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


async def get_person_session(
        cart_type: Union["User", "SessionData", ORJSONResponse] = Depends(user_cookie_or_error),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> Union["Person", "SessionPerson"]:
    service: PersonsService = PersonsService(
        session=session
    )
    print('11111111 dep 27', cart_type, type(cart_type)) #######################################################################################
    return await service.get_one(
        cart_type=cart_type,
        to_schema=False,
    )


async def get_person_session_full(
        cart_type: Union["User", "SessionData", ORJSONResponse] = Depends(user_cookie_or_error),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> Union["Person", "SessionPerson"]:
    service: PersonsService = PersonsService(
        session=session
    )
    return await service.get_one_complex(
        cart_type=cart_type,
        to_schema=False,
    )
