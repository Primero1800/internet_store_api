from typing import TYPE_CHECKING
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer
from .service import CartsService
from ..users.user.dependencies import current_user

if TYPE_CHECKING:
    from src.core.models import Cart, User

CLASS = "Cart"


async def get_one_simple(
    id: int,
    session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "Cart":
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_one(id=id, to_schema=False)


async def get_or_create_cart(
        user: "User" = Depends(current_user),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "Cart":
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_or_create(user_id=user.id)
