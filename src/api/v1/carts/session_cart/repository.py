import logging
from typing import Union, TYPE_CHECKING, Optional

from fastapi.responses import ORJSONResponse

from src.api.v1.sessions.service import SessionsService
from src.core.sessions.fastapi_sessions_config import (
    SessionData,
)
from src.core.settings import settings
from src.tools.exceptions import CustomException
from . import SessionCart, SessionCartItem
from ..exceptions import Errors

if TYPE_CHECKING:
    from ..schemas import (
        CartCreate,
        CartUpdate,
        CartPartialUpdate,
        CartItemCreate,
        CartItemUpdate,
        CartItemPartialUpdate,
    )

CLASS = "SessionCart"
CART = settings.sessions.SESSION_CART


class SessionCartsRepository:
    def __init__(
            self,
            session_data: SessionData
    ):
        self.session_data = session_data
        self.logger = logging.getLogger(__name__)

    async def get_one_complex(
            self,
            cart_type: SessionData,
            id: int = None,
            maximized: bool = True,
            relations: list = []
    ):
        if not CART in cart_type.data:
            text_error = f"user_id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        cart = cart_type.data[CART]
        result = SessionCart(**cart)
        return result

    async def get_all(
            self,
    ) -> list:
        session_service: SessionsService = SessionsService()
        all_sessions = await session_service.get_all()
        result = []
        for session_data in all_sessions:
            if hasattr(session_data, 'data') and CART in session_data.data:
                cart = SessionCart(**session_data.data[CART])
                result.append(cart)
        return result

    async def get_orm_model_from_schema(
            self,
            instance: Union["CartCreate", "CartUpdate", "CartPartialUpdate"],
    ):
        orm_model: SessionCart = SessionCart(**instance.model_dump())
        return orm_model

    async def get_item_orm_model_from_schema(
            self,
            instance: Union["CartItemCreate", "CartItemUpdate"]
    ):
        orm_model: SessionCartItem = SessionCartItem(**instance.model_dump())
        return orm_model

    async def create_one_empty(
            self,
            orm_model: SessionCart
    ):
        session_service: SessionsService = SessionsService()

        result = await session_service.update_session(
            session_data=self.session_data,
            data_to_update={
                CART: orm_model.to_dict()
            },
            session_id=self.session_data.session_id
        )
        if isinstance(result, ORJSONResponse):
            raise CustomException(
                status_code=result.status_code,
                msg=result.content.get("detail")
            )
        result =  SessionCart(**result.data[CART])
        return result

    async def create_one_empty_item(
            self,
            orm_model: SessionCartItem,
    ):

        cart = self.session_data.data[CART]
        cart.setdefault('cart_items', [])
        cart['cart_items'].append(orm_model.to_dict())

        session_service: SessionsService = SessionsService()
        result = await session_service.update_session(
            session_data=self.session_data,
            data_to_update={
                CART: cart
            },
            session_id=self.session_data.session_id
        )
        if isinstance(result, ORJSONResponse):
            raise CustomException(
                status_code=result.status_code,
                msg=result.content.get("detail")
            )

    async def get_one_item_complex(
            self,
            product_id: int,
            cart_id: Optional[int] = None,
            maximized: bool = True,
    ):
        cart = self.session_data.data[CART]

        for cart_item in cart['cart_items']:
            if cart_item['product_id'] == product_id:
                result = await SessionCartsRepository.dict_to_orm(**cart_item)
                return result
        raise CustomException(
            msg=Errors.item_not_exists_id(cart_id=None, product_id=product_id)
        )

    async def clear_cart(
            self,
            cart: SessionCart
    ):
        cart.cart_items.clear()

        session_service: SessionsService = SessionsService()
        result = await session_service.update_session(
            session_data=self.session_data,
            data_to_update={
                CART: cart
            },
            session_id=self.session_data.session_id
        )
        if isinstance(result, ORJSONResponse):
            raise CustomException(
                status_code=result.status_code,
                msg=result.content.get("detail")
            )
        return cart

    @staticmethod
    async def dict_to_orm(
            **kwargs
    ):
        return SessionCartItem(**kwargs)

    async def edit_cart_item(
            self,
            orm_model: SessionCartItem,
            instance: Union["CartItemUpdate", "CartItemPartialUpdate"],
            is_partial: bool = False
    ):
        for key, val in instance.model_dump(
                exclude_unset=is_partial,
                exclude_none=is_partial,
        ).items():
            setattr(orm_model, key, val)

        self.logger.warning(f"Editing %r in database" % orm_model)

        cart = self.session_data.data[CART]
        cart_items = cart['cart_items']

        # Ищем индекс элемента с нужным product_id
        index_to_replace = -1
        for i, item in enumerate(cart_items):
            if item.get("product_id") == orm_model.product_id:
                index_to_replace = i
                break
        # Если элемент найден, заменяем его
        if index_to_replace != -1:
            cart_items[index_to_replace] = orm_model.to_dict()

        session_service: SessionsService = SessionsService()
        result = await session_service.update_session(
            session_data=self.session_data,
            data_to_update={
                CART: cart
            },
            session_id=self.session_data.session_id
        )
        if isinstance(result, ORJSONResponse):
            raise CustomException(
                status_code=result.status_code,
                msg=result.content.get("detail")
            )

        return orm_model

    async def delete_cart_item(
            self,
            orm_model: SessionCartItem,
    ) -> None:

        cart = self.session_data.data[CART]
        cart_items = cart['cart_items']

        if isinstance(orm_model, SessionCartItem):  # Отфильтровываем элемент с равным product_id
            cart['cart_items'] = [item for item in cart_items if item['product_id'] != orm_model.product_id]

        session_service: SessionsService = SessionsService()
        result = await session_service.update_session(
            session_data=self.session_data,
            data_to_update={
                CART: cart
            },
            session_id=self.session_data.session_id
        )
        if isinstance(result, ORJSONResponse):
            raise CustomException(
                status_code=result.status_code,
                msg=result.content.get("detail")
            )
