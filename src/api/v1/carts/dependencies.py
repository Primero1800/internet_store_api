from typing import TYPE_CHECKING, Union
from fastapi import Depends, Form, status
from fastapi.responses import ORJSONResponse
from fastapi_sessions.backends.session_backend import BackendError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer
from src.core.sessions.fastapi_sessions_config import verifier_or_none, SessionData
from .service import CartsService
from .exceptions import Errors
from ..users.user.dependencies import current_user, current_user_or_none

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


async def user_cookie_or_error(
        user: "User" = Depends(current_user_or_none),
        session_data: SessionData = Depends(verifier_or_none),
) -> Union["User", SessionData, ORJSONResponse]:
    if user:
        return user
    if session_data and not isinstance(session_data, BackendError):
        return session_data
    return ORJSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "message": Errors.HANDLER_MESSAGE,
            "detail": "No authentication or session provided",
        }
    )


async def get_or_create_cart_sessioned(
        cart_type: Union["User", SessionData, ORJSONResponse] = Depends(user_cookie_or_error),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> Union["Cart", "SessionCart"]:
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_or_create(cart_type=cart_type)


async def get_or_create_cart_item_sessioned(
        product_id: int = Form(gt=0),
        cart: Union["Cart", "SessionCart"] = Depends(get_or_create_cart_sessioned),
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

