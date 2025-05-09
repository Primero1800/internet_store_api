from typing import TYPE_CHECKING
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer
from .service import OrdersService
from ...users.user.dependencies import current_user

if TYPE_CHECKING:
    from src.core.models import Order, User

CLASS = "Order"


async def get_one_simple(
    id: int,
    user: "User" = Depends(current_user),
    session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "Order":
    service: OrdersService = OrdersService(
        session=session
    )
    return await service.get_one(
        id=id,
        user=user,
        to_schema=False
    )

async def get_one_complex(
    id: int,
    user: "User" = Depends(current_user),
    session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "Order":
    service: OrdersService = OrdersService(
        session=session
    )
    return await service.get_one_complex(
        id=id,
        user=user,
        to_schema=False
    )
