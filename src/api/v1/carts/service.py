import logging
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Iterable, Any, Union

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.sessions.fastapi_sessions_config import SessionData
from src.tools.exceptions import CustomException
from . import utils
from ..store.products import utils as product_utils
from .repository import CartsRepository
from .schemas import (
    CartCreate,
    CartUpdate,
    CartPartialUpdate,
    CartItemCreate,
    CartItemPartialUpdate,
)
from .exceptions import Errors
from .session_cart.repository import SessionCartsRepository
from .validators import ValidRelationsInspector


if TYPE_CHECKING:
    from src.core.models import (
        Cart,
        Product,
        CartItem,
    )
    from src.api.v1.carts.session_cart import (
        SessionCart,
        SessionCartItem,
    )
    from .filters import CartFilter

CLASS = "Cart"
_CLASS = "cart"


class CartsService:
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
            filter_model: "CartFilter",
            db_carts: Optional[bool] = None
    ):
        result = []
        if db_carts is True or db_carts is None:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )
            listed_orm_models = await repository.get_all(filter_model=filter_model)
            for orm_model in listed_orm_models:
                result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        if db_carts is False or db_carts is None:
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=self.session_data
            )
            listed_orm_models = await repository.get_all()
            for orm_model in listed_orm_models:
                result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "CartFilter",
            db_carts: Optional[bool] = None
    ):
        result = []
        if db_carts is True or db_carts is None:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )
            listed_orm_models = await repository.get_all_full(filter_model=filter_model)
            for orm_model in listed_orm_models:
                result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        if db_carts is False or db_carts is None:
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=self.session_data
            )
            listed_orm_models = await repository.get_all()
            for orm_model in listed_orm_models:
                result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        return result

    async def get_one(
            self,
            id: int,
            to_schema: bool = True
    ):
        repository: CartsRepository = CartsRepository(
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
        if to_schema:
            return await utils.get_short_schema_from_orm(orm_model=returned_orm_model)
        return returned_orm_model

    async def get_one_complex(
            self,
            id: int = None,
            cart_type: Any = None,
            maximized: bool = True,
            relations: list | None = None,
            to_schema: bool = True,
    ):
        if isinstance(cart_type, ORJSONResponse):
            return cart_type
        if cart_type and isinstance(cart_type, SessionData):
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=cart_type
            )
        else:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )
        try:
            returned_orm_model = await repository.get_one_complex(
                id=id,
                cart_type=cart_type,
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
            id: int = None,
            cart_type: Any = None,
            to_schema: bool = True
    ):
        if cart_type and isinstance(cart_type, SessionData):
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=cart_type
            )
        else:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )

        # catching ValidationError in exception_handler
        instance: CartCreate = CartCreate(
            user_id=id,
        )
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

        dict_to_validate = {}
        if isinstance(id, int):
            dict_to_validate['user_id'] = id
        inspector = ValidRelationsInspector(
            session=self.session,
            **dict_to_validate
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result

        try:
            await repository.create_one_empty(orm_model=orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        self.logger.info("%s %r was successfully created" % (CLASS, orm_model))
        return await self.get_one_complex(
            id=orm_model.user_id,
            cart_type=cart_type,
            to_schema=to_schema
        )

    async def delete_one(
            self,
            orm_model: "Cart",
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: CartsRepository = CartsRepository(
            session=self.session
        )

        try:
            return await repository.delete_one(orm_model=orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

    async def edit_one(
            self,
            orm_model: "Cart",
            id: int,
            is_partial: bool = False
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model
        repository: CartsRepository = CartsRepository(
            session=self.session,
        )

        # catching ValidationError in exception_handler
        updating_dictionary = {
            "user_id": id
        }
        if is_partial:
            instance: CartPartialUpdate = CartPartialUpdate(**updating_dictionary)
        else:
            instance: CartUpdate = CartUpdate(**updating_dictionary)

        dict_to_validate = {}
        if isinstance(id, int):
            dict_to_validate['user_id'] = id
        inspector = ValidRelationsInspector(
            session=self.session,
            **dict_to_validate
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result

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
            id=orm_model.user_id
        )

    async def get_or_create(
            self,
            user_id: Optional[int] = None,
            cart_type: Optional[Any] = None,
            to_schema: bool = False,
            maximized: bool = False,
    ):

        if isinstance(cart_type, ORJSONResponse):
            return cart_type

        logger_user_id = user_id if user_id else None
        if not logger_user_id:
            logger_user_id = cart_type.id if hasattr(cart_type, 'id') else cart_type.user_id

        self.logger.info('Getting %r bound with user_id=%s from database' % (CLASS, logger_user_id))
        sa_orm_model = await self.get_one_complex(
            id=user_id,
            cart_type=cart_type,
            to_schema=False
        )
        if isinstance(sa_orm_model, ORJSONResponse):
            self.logger.info('No %r bound with user_id=%s in database' % (CLASS, logger_user_id))
            self.logger.info('Creating %r bound with user_id=%s in database' % (CLASS, logger_user_id))
            sa_orm_model = await self.create_one(
                id=user_id,
                cart_type=cart_type,
                to_schema=False,
            )

        if to_schema:
            if not maximized:
                return await utils.get_short_schema_from_orm(sa_orm_model)
            else:
                return await utils.get_schema_from_orm(sa_orm_model)
        return sa_orm_model

    async def get_or_create_item(
            self,
            product_id: int,
            user_id: Optional[int] = None,
            cart: Optional[Union["Cart", "SessionCart"]] = None,
            to_schema: bool = False,
            maximized: bool = False,
    ):
        if not cart:
            cart: Union["Cart", "SessionCart"] = await self.get_or_create(
                user_id=user_id
            )
        self.logger.info('Getting %sItem from %s' % (CLASS, CLASS))

        item_orm_model = await self.get_one_item_complex(
            cart=cart,
            product_id=product_id,
        )
        if isinstance(item_orm_model, ORJSONResponse):
            self.logger.info(
                'No %sItem with cart_id=%s and product_id=%s in database' % (CLASS, cart.user_id, product_id)
            )
            self.logger.info(
                'Creating %sItem with cart_id=%s and product_id=%s in database' % (CLASS, cart.user_id, product_id)
            )
            item_orm_model = await self.create_one_item(
                cart=cart,
                product_id=product_id,
                to_schema=False,
            )

        if to_schema:
            if not maximized:
                return await utils.get_short_item_schema_from_orm(item_orm_model)
            else:
                return await utils.get_item_schema_from_orm(item_orm_model)
        return item_orm_model

    async def get_one_item_complex(
            self,
            cart: Union["Cart", "SessionCart"],
            product_id: int,
    ):
        if hasattr(cart, "cart_items") and isinstance(cart.cart_items, Iterable):
            for cart_item in cart.cart_items:
                product_id_to_compare = cart_item.product_id
                if product_id_to_compare == product_id:
                    return cart_item
        return ORJSONResponse(
            content={
                "message": Errors.HANDLER_MESSAGE(),
                "detail": Errors.item_not_exists_id(cart.user_id, product_id)
            }
        )

    async def get_one_item_from_db(
            self,
            product_id: int,
            cart_id: int,
            maximized: bool = True,
            to_schema: bool = False
    ):
        if cart_id is None:
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=self.session_data
            )
        else:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )
        try:
            returned_orm_model = await repository.get_one_item_complex(
                cart_id=cart_id,
                product_id=product_id,
                maximized=maximized,
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
            if not maximized:
                return await utils.get_short_item_schema_from_orm(
                    returned_orm_model
                )
            return await utils.get_item_schema_from_orm(
                returned_orm_model,
            )
        return returned_orm_model

    async def create_one_item(
            self,
            cart: Union["Cart", "SessionCart"],
            product_id: int,
            quantity: int = 1,
            to_schema: bool = True,
            original_price: Optional[Decimal] = None
    ):
        if cart.user_id is not None:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )
        else:
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=self.session_data
            )

        dict_to_validate = {
            'product_id': product_id
        }
        inspector = ValidRelationsInspector(
            session=self.session,
            **dict_to_validate
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result
        product_orm = result["product_orm"] if "product_orm" in result else None

        quantity = min(quantity, product_orm.quantity)
        if not product_orm.available or quantity < 1:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": f"Item can't be added to {CLASS}: not enough quantity",
                }
            )

        # catching ValidationError in exception_handler
        instance: CartItemCreate = CartItemCreate(
            product_id=product_orm.id,
            price=original_price if original_price else product_orm.price,
            cart_id=cart.user_id,
            quantity=quantity,
        )
        orm_model = await repository.get_item_orm_model_from_schema(instance=instance)

        if orm_model.cart_id is None:           # Is SessionCartItem
            orm_model.product = (await product_utils.get_short_schema_from_orm(product_orm)).model_dump()

        try:
            await repository.create_one_empty_item(
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

        self.logger.info("%sItem %r was successfully created" % (CLASS, orm_model))
        return await self.get_one_item_from_db(
            cart_id=cart.user_id,
            product_id=product_id,
            to_schema=to_schema
        )

    async def clear_cart(
            self,
            cart: Optional[Union["Cart", "SessionCart"]] = None,
            user_id: Optional[int] = None,
            to_schema: bool = True
    ):
        if not cart:
            cart: "Cart" = await self.get_or_create(
                user_id=user_id
            )
        if isinstance(cart, ORJSONResponse):
            return cart

        if not cart.user_id:
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=self.session_data
            )
        else:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )

        try:
            orm_model = await repository.clear_cart(
                cart=cart
            )
        except CustomException as exc:
            self.logger.error(Errors.DATABASE_ERROR(), exc_info=exc)
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
        if to_schema:
            return await utils.get_short_schema_from_orm(orm_model)
        return orm_model

    async def change_quantity(
            self,
            delta: Optional[int] = None,
            absolute: Optional[int] = None,
            cart_item: Optional[Union["CartItem", "SessionCartItem"]] = None,
            user_id: Optional[int] = None,
            product_id: Optional[int] = None,
            to_schema: bool = True,
    ):
        if not cart_item:
            cart_item: Union["CartItem", "SessionCartItem"] = await self.get_or_create_item(
                product_id=product_id,
                user_id=user_id,
            )
        if isinstance(cart_item, ORJSONResponse):
            return cart_item
        dict_to_validate = {
            'product_id': cart_item.product_id
        }
        inspector = ValidRelationsInspector(
            session=self.session,
            **dict_to_validate
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result
        product_orm: "Product" = result["product_orm"] if "product_orm" in result else None

        new_quantity = (cart_item.quantity + delta) if delta else absolute
        new_quantity = min(new_quantity, product_orm.quantity)
        if cart_item.cart_id:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )
        else:
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=self.session_data
            )
        if new_quantity <= 0 or not product_orm.available:
            if product_orm.available:
                self.logger.warning("New product quantity <= 0. CartItem will be deleted from cart")
            else:
                self.logger.warning("Chosen product is not available. CartItem will be deleted from cart")
            try:
                return await repository.delete_cart_item(cart_item)
            except CustomException as exc:
                return ORJSONResponse(
                    status_code=exc.status_code,
                    content={
                        "message": Errors.HANDLER_MESSAGE(),
                        "detail": exc.msg,
                    }
                )

        self.logger.info("New CartItem quantity will be set on %s" % new_quantity)
        instance: CartItemPartialUpdate = CartItemPartialUpdate(
            quantity=new_quantity
        )

        try:
            orm_model = await repository.edit_cart_item(
                instance=instance,
                orm_model=cart_item,
                is_partial=True,
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
            return await utils.get_short_item_schema_from_orm(orm_model)
        return orm_model

    async def delete_item(
            self,
            cart: Union["Cart", "SessionCart"],
            product_id: int
    ):

        if isinstance(cart, ORJSONResponse):
            return cart

        if cart.user_id:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )
        else:
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=self.session_data
            )
        try:
            item_orm_model = await repository.get_one_item_complex(
                cart_id=cart.user_id,
                product_id=product_id,
                maximized=False,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
        try:
            return await repository.delete_cart_item(orm_model=item_orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

    async def sum_carts(
            self,
            user_cart: "Cart",
            session_cart: "SessionCart"
    ):

        for cart_item in session_cart.cart_items:

            orm_model_item = await self.get_one_item_complex(
                cart=user_cart,
                product_id=cart_item.product_id,
            )

            if isinstance(orm_model_item, ORJSONResponse):  # Item doesn't exist in Cart
                orm_model_item = await self.create_one_item(
                    cart=user_cart,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    original_price=cart_item.price,
                    to_schema=False
                )
                if isinstance(orm_model_item, ORJSONResponse):
                    self.logger.error("Error occurred while replacing item from SessionCart to Cart")
                else:
                    self.logger.info("New CartItem was successfully created according SessionCartItem")

            else:           # Item already exists in Cart
                orm_model_item = await self.change_quantity(
                    absolute=orm_model_item.quantity + cart_item.quantity,
                    cart_item=orm_model_item,
                    to_schema=False
                )
                if isinstance(orm_model_item, ORJSONResponse):
                    self.logger.error("Error occurred while changing quantity of item in Cart according SessionCart")
                else:
                    self.logger.info("CartItem's quantity was successfully created according SessionCartItem")

        # Clearing SessionCart after adding items to Cart
        repository: SessionCartsRepository = SessionCartsRepository(
            session_data=self.session_data
        )
        await repository.clear_cart(
            cart=session_cart
        )
        self.logger.info("SessionCart was successfully cleared after adding items to Cart")

    async def normalize_items_quantity(
            self,
            cart: Union["Cart", "SessionCart"],
            return_none: bool = True
    ):
        self.logger.warning("Normalizing cart items quantity according product quantity before ordering")
        for cart_item in cart.cart_items:
            orm_model = await self.change_quantity(
                cart_item=cart_item,
                absolute=cart_item.quantity,
                to_schema=False,
            )
            if isinstance(orm_model, ORJSONResponse):
                self.logger.error("Error occurred while normalizing item quantity")
        if return_none:
            return
        return await self.get_cart_items(
            cart_id=cart.user_id,
            cart_type=self.session_data if not cart.user_id else None,
        )

    async def get_cart_items(
            self,
            cart_id: int | None = None,
            cart_type: Any = None,
    ):
        if not cart_id:
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=cart_type
            )
        else:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )
        try:
            return await repository.get_cart_items(
                cart_id=cart_id,
                cart_type=cart_type,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
