from typing import Union, TYPE_CHECKING

from fastapi import Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.users.user.dependencies import user_cookie_or_error
from src.core.config import DBConfigurer

from .service import AddressesService

if TYPE_CHECKING:
    from src.core.models import (
        Address,
        User,
    )
    from src.core.sessions.fastapi_sessions_config import SessionData
    from .session_address import SessionAddress


async def get_one_session(
        obj_type: Union["User", "SessionData", ORJSONResponse] = Depends(user_cookie_or_error),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> Union["Address", "SessionAddress"]:
    service: AddressesService = AddressesService(
        session=session
    )
    return await service.get_one(
        obj_type=obj_type,
        to_schema=False,
    )


async def get_one_session_full(
        obj_type: Union["User", "SessionData", ORJSONResponse] = Depends(user_cookie_or_error),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> Union["Address", "SessionAddress"]:
    service: AddressesService = AddressesService(
        session=session
    )
    return await service.get_one_complex(
        obj_type=obj_type,
        to_schema=False,
    )


async def get_one_simple(
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "Address":
    service: AddressesService = AddressesService(
        session=session
    )
    return await service.get_one(
        user_id=user_id,
        to_schema=False,
    )
