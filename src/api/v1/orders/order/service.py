import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Any, Union

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.sessions.fastapi_sessions_config import SessionData
from src.tools.exceptions import CustomException
from src.tools.status_choices import StatusChoices
from . import utils
from .repository import OrdersRepository
from .schemas import (
    OrderCreate,
    OrderUpdate,
    OrderPartialUpdate,
)
from .exceptions import Errors

if TYPE_CHECKING:
    from src.core.models import (
        User,
        Cart,
        Address,
        Person,
        Order,
    )
    from src.api.v1.carts.session_cart import (
        SessionCart,
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
            relations: list | None = None,
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

        from src.api.v1.carts.utils import (
            serve_normalize_item_quantity,
            clear_cart
        )
        new_items = await serve_normalize_item_quantity(
            cart=cart,
            session=self.session,
            session_data=self.session_data
        )
        if isinstance(new_items, ORJSONResponse):
            return new_items

        # if not cart.cart_items:
        if not new_items:
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": 'Cart is empty. Impossible to create order',
                }
            )

        # Expecting if OrderCreate data valid
        # catching ValidationError in exception_handler
        order_content = await utils.get_normalized_order_content(new_items)
        total_cost = await utils.get_normalized_total_cost(cart)

        instance: OrderCreate = OrderCreate(
            user_id=user.id if user else None,
            total_cost=total_cost,
            phonenumber=address.phonenumber,
            order_content=order_content,
            person_content=person.to_dict(),
            address_content=address.to_dict(),
            move_to=move_to,
            payment_conditions=payment_ways,
            time_placed=datetime.now(),
        )

        result = await self.reserve_products_from_cart(cart_items=new_items)
        if isinstance(result, ORJSONResponse):
            return result

        cleared_cart = await clear_cart(
            cart=cart,
            session=self.session,
            session_data=self.session_data,
        )
        if isinstance(cleared_cart, ORJSONResponse):
            return cleared_cart

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

    async def reserve_products_from_cart(
            self,
            cart_items: list[Any],
            cart: Optional[Union["Cart", "SessionCart"]] = None,
    ):
        if cart:
            cart_items = cart.cart_items

        self.logger.info("Reserving products from cart for order")
        from src.api.v1.store.products.utils import change_quantity
        for item in cart_items:
            result = await change_quantity(
                id=item.product_id if hasattr(item, "product_id") else item['product_id'],
                reserved_quantity=item.quantity if hasattr(item, 'quantity') else item['quantity'],
                session=self.session
            )
            if isinstance(result, ORJSONResponse):
                self.logger.error('Error occurred while reserving products from cart')
                return result

    async def deliver_one(
            self,
            user: "User",
            orm_model: "Order",
            return_none: bool = True,
            to_schema: bool = True,
    ):
        if isinstance(orm_model, ORJSONResponse):
            return orm_model

        if orm_model.status != StatusChoices.S_ORDERED:
            self.logger.error("Attempt to serve 'delivery' for %s with id=%s with status=%s" % (
                CLASS, orm_model.id, orm_model.status)
                              )
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": "%s with id=%s and status=%s is unacceptable for chosen service, "
                              "because already processed" % (CLASS, orm_model.id, orm_model.status),
                }
            )

        # Expecting if OrderPartialUpdate data valid
        # catching ValidationError in exception_handler
        instance: OrderPartialUpdate = OrderPartialUpdate(
            **orm_model.to_dict()
        )
        instance.time_delivered = datetime.now()
        instance.status = StatusChoices.S_DELIVERED

        products_content_list = [
            {item['product']['id']: item['quantity']} for item in orm_model.order_content
        ]
        result = await self.serve_deliver(
            products_content_list=products_content_list,
        )
        if isinstance(result, ORJSONResponse):
            return result

        repository: OrdersRepository = OrdersRepository(
            session=self.session
        )
        try:
            await repository.edit_one_empty(
                instance=instance,
                orm_model=orm_model,
                is_partial=True
            )
        except CustomException as exc:
            self.logger.error('Error occurred while editing %s in database' % CLASS, exc_info=exc)
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        if return_none:
            return
        return await self.get_one_complex(
            user=user,
            id=orm_model.id,
            to_schema=to_schema
        )

    async def serve_deliver(
            self,
            products_content_list: list[Any]
    ):
        from src.api.v1.store.sale_information.service import SaleInfoService
        sa_service: SaleInfoService = SaleInfoService(
            session=self.session
        )
        for item in products_content_list:
            for product_id, sold_quantity in item.items():
                sa_orm = await sa_service.get_or_create(
                    product_id=product_id,
                )
                if isinstance(sa_orm, ORJSONResponse):
                    self.logger.error(
                        "Error occurred while serving 'delivery': %s" % json.loads(sa_orm.body.decode()).get('detail'),
                    )
                    # return sa_orm
                else:
                    sa_orm_modified = await sa_service.edit_one(
                        product_id=product_id,
                        orm_model=sa_orm,
                        sold_count=sa_orm.sold_count + sold_quantity,
                        is_partial=True,
                        to_schema=False,
                    )
                    if isinstance(sa_orm_modified, ORJSONResponse):
                        self.logger.error("Error occurred while serving 'delivery': %s"
                                          % json.loads(sa_orm_modified.body.decode()).get('detail'))
                    # return sa_orm_modified
        return True

    async def cancel_one(
            self,
            user: "User",
            orm_model: "Order",
            return_none: bool = True,
            to_schema: bool = True,
    ):
        if isinstance(orm_model, ORJSONResponse):
            return orm_model

        if orm_model.status != StatusChoices.S_ORDERED:
            self.logger.error("Attempt to serve 'cancel' for %s with id=%s with status=%s" % (
                CLASS, orm_model.id, orm_model.status)
                              )
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": "%s with id=%s and status=%s is unacceptable for chosen service, "
                              "because already processed" % (CLASS, orm_model.id, orm_model.status),
                }
            )

        # Expecting if OrderPartialUpdate data valid
        # catching ValidationError in exception_handler
        instance: OrderPartialUpdate = OrderPartialUpdate(
            **orm_model.to_dict()
        )
        instance.time_delivered = datetime.now()
        instance.status = StatusChoices.S_CANCELLED

        products_content_list = [
            {item['product']['id']: item['quantity']} for item in orm_model.order_content
        ]
        result = await self.serve_cancel(
            products_content_list=products_content_list,
        )
        if isinstance(result, ORJSONResponse):
            return result

        repository: OrdersRepository = OrdersRepository(
            session=self.session
        )
        try:
            await repository.edit_one_empty(
                instance=instance,
                orm_model=orm_model,
                is_partial=True
            )
        except CustomException as exc:
            self.logger.error('Error occurred while editing %s in database' % CLASS, exc_info=exc)
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        if return_none:
            return
        return await self.get_one_complex(
            user=user,
            id=orm_model.id,
            to_schema=to_schema
        )

    async def serve_cancel(
            self,
            products_content_list: list[Any]
    ):
        from src.api.v1.store.products.service import ProductsService
        p_service: ProductsService = ProductsService(
            session=self.session
        )
        for item in products_content_list:
            for product_id, back_quantity in item.items():
                orm_model = await p_service.get_one(
                    id=product_id,
                    to_schema=False
                )
                if isinstance(orm_model, ORJSONResponse):
                    self.logger.error(
                        "Error occurred while serving 'delivery': %s" %
                        json.loads(orm_model.body.decode()).get('detail'),
                    )
                    # return orm_model
                else:
                    orm_model_modified = await p_service.edit_one(
                        orm_model=orm_model,
                        quantity=orm_model.quantity + back_quantity,
                        is_partial=True,
                    )
                    if isinstance(orm_model_modified, ORJSONResponse):
                        self.logger.error("Error occurred while serving 'delivery': %s"
                                          % json.loads(orm_model_modified.body.decode()).get('detail'))
                    # return sa_orm_modified
        return True
