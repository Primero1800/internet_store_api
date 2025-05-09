from typing import TYPE_CHECKING, Union
from fastapi import Depends, Form
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer
from src.core.sessions.fastapi_sessions_config import verifier_or_none, SessionData
from .service import CartsService
from ..users.user.dependencies import (
    current_user,
    user_cookie_or_error,
)

if TYPE_CHECKING:
    from src.core.models import Cart, User, CartItem
    from src.api.v1.carts.session_cart import SessionCart

CLASS = "Cart"


async def get_one_simple(
    id: int,
    session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "Cart":
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_one(id=id, to_schema=False)


async def get_one_complex_session(
        cart_type: Union["User", SessionData, ORJSONResponse] = Depends(user_cookie_or_error),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        session_data: SessionData = Depends(verifier_or_none),
):
    service: CartsService = CartsService(
        session=session,
        session_data=session_data
    )
    return await service.get_one_complex(
        cart_type=cart_type,
        to_schema=False,
    )


async def get_or_create_cart(
        user: "User" = Depends(current_user),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "Cart":
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_or_create(user_id=user.id)


async def get_or_create_cart_item(
        product_id: int = Form(gt=0),
        cart: "Cart" = Depends(get_or_create_cart),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "CartItem":
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_or_create_item(
        cart=cart,
        product_id=product_id
    )


async def get_or_create_cart_session(
        cart_type: Union["User", SessionData, ORJSONResponse] = Depends(user_cookie_or_error),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> Union["Cart", "SessionCart"]:
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_or_create(cart_type=cart_type)


async def get_or_create_cart_item_session(
        product_id: int = Form(gt=0),
        cart: Union["Cart", "SessionCart"] = Depends(get_or_create_cart_session),
        session_data: SessionData = Depends(verifier_or_none),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "CartItem":
    service: CartsService = CartsService(
        session=session,
        session_data=session_data
    )
    return await service.get_or_create_item(
        cart=cart,
        product_id=product_id
    )
