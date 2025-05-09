import logging
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Iterable, Any, Union

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.sessions.fastapi_sessions_config import SessionData
from src.tools.exceptions import CustomException
from . import utils
from .repository import OrdersRepository
from .schemas import (
    OrderCreate,
    OrderUpdate,
    OrderPartialUpdate,
)
from .exceptions import Errors
from .validators import ValidRelationsInspector


if TYPE_CHECKING:
    from src.core.models import (
        User,
        Cart,
        CartItem,
        Address,
        Person,
        Order,
        Product,
    )
    from src.api.v1.carts.session_cart import (
        SessionCart,
        SessionCartItem,
    )
    from ..address.session_address import SessionAddress
    from ..person.session_person import SessionPerson
    from .filters import OrderFilter

CLASS = "Order"
_CLASS = "order"


class OrdersService:
    def __init__(
            self,
            session: AsyncSession,
            session_data: Optional[SessionData] = None
    ):
        self.session = session
        self.session_data = session_data
        self.logger = logging.getLogger(__name__)

    async def create_one(
            self,
            user: Union["User", None],
            cart: Union["Cart", "SessionCart", ORJSONResponse],
            address: Union["Address", "SessionAddress", ORJSONResponse],
            person: Union['Person', "SessionPerson", ORJSONResponse],
            move_to: int,
            payment_ways: int,
            to_schema: bool = False,
    ):
        if isinstance(cart, ORJSONResponse):
            return cart
        if isinstance(person, ORJSONResponse):
            return person
        if isinstance(address, ORJSONResponse):
            return address
        if not cart.cart_items:
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": 'Cart is empty. Impossible to create order',
                }
            )

        # Expecting if OrderCreate data valid
                # catching ValidationError in exception_handler
        order_content = await utils.get_normalized_order_content(cart)
        total_cost = await utils.get_normalized_total_cost(cart)

        instance: OrderCreate = OrderCreate(
            user_id = user.id if user else None,
            total_cost=total_cost,
            phonenumber=address.phonenumber,
            order_content=order_content,
            person_content=person.to_dict(),
            address_content=address.to_dict(),
            move_to=move_to,
            payment_conditions=payment_ways,
            time_placed=datetime.now(),
        )

        repository: OrdersRepository = OrdersRepository(
            session=self.session,
        )

        orm_model = await repository.get_orm_model_from_schema(instance=instance)

        try:
            orm_model = await repository.create_one(
                orm_model=orm_model,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        if to_schema:
            return await utils.get_schema_from_orm(orm_model)
        return orm_model
