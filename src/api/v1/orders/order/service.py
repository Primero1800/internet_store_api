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


    async def get_all(
            self,
            filter_model: "OrderFilter",
            user_id: Optional[int] = None,
    ):
        repository: OrdersRepository = OrdersRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(
            filter_model=filter_model,
            user_id=user_id,
        )
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "OrderFilter",
            user_id: Optional[int] = None,
    ):
        repository: OrdersRepository = OrdersRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all_full(
            filter_model=filter_model,
            user_id=user_id
        )
        for orm_model in listed_orm_models:
            result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        return result

    async def get_one(
            self,
            user: "User",
            id: int,
            to_schema: bool = True
    ):
        repository: OrdersRepository = OrdersRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one(
                id=id,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
        if not user.is_superuser and user.id != returned_orm_model.user_id:
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": Errors.NO_RIGHTS(),
                }
            )
        if to_schema:
            return await utils.get_short_schema_from_orm(returned_orm_model)
        return returned_orm_model

    async def get_one_complex(
            self,
            user: "User",
            id: int = None,
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        repository: OrdersRepository = OrdersRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one_complex(
                id=id,
                maximized=maximized,
                relations=relations,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
        if not user.is_superuser and user.id != returned_orm_model.user_id:
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": Errors.NO_RIGHTS(),
                }
            )
        if to_schema:
            if not maximized and not relations:
                return await utils.get_short_schema_from_orm(
                    returned_orm_model
                )
            return await utils.get_schema_from_orm(
                returned_orm_model,
                maximized=maximized,
                relations=relations,
            )
        return returned_orm_model

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

    async def edit_one(
            self,
            orm_model: "Order",
            user: "User",
            move_to: Optional[int] = None,
            payment_conditions: Optional[int] = None,
            is_partial: bool = False,
    ):
        if isinstance(orm_model, ORJSONResponse):
            return orm_model
        if ((not isinstance(move_to, int) and not isinstance(payment_conditions, int)) or
            (move_to == orm_model.move_to and payment_conditions == orm_model.payment_conditions)):
            return await utils.get_schema_from_orm(orm_model)

        updating_dictionary = {
            "move_to": move_to,
            "payment_conditions": payment_conditions,
        }
        if is_partial:
            instance: OrderPartialUpdate = OrderPartialUpdate(**updating_dictionary)
        else:
            instance: OrderUpdate = OrderUpdate(**updating_dictionary)

        repository: OrdersRepository = OrdersRepository(
            session=self.session,
        )
        try:
            await repository.edit_one_empty(
                instance=instance,
                orm_model=orm_model,
                is_partial=is_partial,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        self.logger.info("%s %r was successfully edited" % (CLASS, orm_model))

        return await self.get_one_complex(
            user=user,
            id=orm_model.id,
        )
