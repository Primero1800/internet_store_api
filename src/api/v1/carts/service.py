import logging
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
        User,
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
    ):
        repository: CartsRepository = CartsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "CartFilter"
    ):
        repository: CartsRepository = CartsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all_full(filter_model=filter_model)
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
                    "message": Errors.HANDLER_MESSAGE,
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
            relations: list | None = [],
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
                    "message": Errors.HANDLER_MESSAGE,
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
                    "message": Errors.HANDLER_MESSAGE,
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
                    "message": Errors.HANDLER_MESSAGE,
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
        # product_orm = result["product_orm"] if "product_orm" in result else None

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
                    "message": Errors.HANDLER_MESSAGE,
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

        self.logger.info('Getting %r bound with user_id=%s from database' % (CLASS, user_id))
        sa_orm_model = await self.get_one_complex(
            id=user_id,
            cart_type=cart_type,
            to_schema=False
        )
        if isinstance(sa_orm_model, ORJSONResponse):
            self.logger.info('No %r bound with user_id=%s in database' % (CLASS, user_id))
            self.logger.info('Creating %r bound with user_id=%s in database' % (CLASS, user_id))
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
        print('111111111111111111 ser 312', cart, type(cart)) #######################################################################################
        if not cart:
            cart: Union["Cart", "SessionCart"] = await self.get_or_create(
                user_id=user_id
            )
        self.logger.info('Getting %sItem from %s' % (CLASS, CLASS))

        item_orm_model = await self.get_one_item_complex(
            cart=cart,
            product_id=product_id,
            to_schema=False
        )
        if isinstance(item_orm_model, ORJSONResponse):
            self.logger.info(
                'No %sItem bound with cart_id=%s and product_id=%s in database' % (CLASS, cart.user_id, product_id)
            )
            self.logger.info(
                'Creating %sItem bound with cart_id=%s and product_id=%s in database' % (CLASS, cart.user_id, product_id)
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
            to_schema: bool = False
    ):
        if hasattr(cart, "cart_items") and isinstance(cart.cart_items, Iterable):
            print('222222222222222 ser 353    CART_ITEMS:', cart.cart_items) ###########################################################################
            for cart_item in cart.cart_items:
                product_id_to_compare = cart_item.product_id if cart.user_id else cart_item['product_id']
                if product_id_to_compare == product_id:
                    print('222222 ser 357           cart_item', cart_item) #############################################
                    return cart_item if cart.user_id else await SessionCartsRepository.dict_to_orm(**cart_item)
        return ORJSONResponse(
            content={
                "message": Errors.HANDLER_MESSAGE,
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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        print('99999999 ser 393 ret_orm_mod', returned_orm_model) ########################################################
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
            to_schema: bool = True
    ):
        if not cart.user_id is None:
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
        print('33333333 ser 422 inspector result', result) ####################################################################################
        if isinstance(result, ORJSONResponse):
            return result
        product_orm = result["product_orm"] if "product_orm" in result else None
        print('33333333 ser 426 prod_orm', result)  ####################################################################################

        if not product_orm.available or product_orm.quantity < quantity:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": f"Item can't be added to {CLASS}: not enough quantity",
                }
            )

        # catching ValidationError in exception_handler
        instance: CartItemCreate = CartItemCreate(
            product_id=product_orm.id,
            price=product_orm.price,
            cart_id=cart.user_id,
            quantity=quantity,
        )
        orm_model = await repository.get_item_orm_model_from_schema(instance=instance)

        if orm_model.cart_id is None:           # Is SessionCartItem
            orm_model.product = (await product_utils.get_short_schema_from_orm(product_orm)).model_dump()
        print('3333333333333 ser 435    ORM_MODEL', orm_model, type(orm_model)) ########################################################################

        try:
            await repository.create_one_empty_item(
                orm_model=orm_model,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
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
            to_schema: bool = False
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
            self.logger.error(Errors.DATABASE_ERROR, exc_info=exc)
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
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
        if cart_item.cart_id:
            repository: CartsRepository = CartsRepository(
                session=self.session
            )
        else:
            repository: SessionCartsRepository = SessionCartsRepository(
                session_data=self.session_data
            )
        if new_quantity <= 0:
            self.logger.warning("New product quantity <= 0. CartItem will be deleted from cart")
            try:
                return await repository.delete_cart_item(cart_item)
            except CustomException as exc:
                return ORJSONResponse(
                    status_code=exc.status_code,
                    content={
                        "message": Errors.HANDLER_MESSAGE,
                        "detail": exc.msg,
                    }
                )

        new_quantity = min(new_quantity, product_orm.quantity)
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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        if to_schema:
            return await utils.get_short_item_schema_from_orm(orm_model)
        return orm_model

    async def delete_item(
            self,
            cart: "Cart",
            product_id: int
    ):
        repository: CartsRepository = CartsRepository(
            session=self.session
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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        try:
            return await self.delete_one(orm_model=item_orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

