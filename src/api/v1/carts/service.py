import logging
from typing import TYPE_CHECKING, Optional, Iterable

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import CartsRepository
from .schemas import (
    CartCreate,
    CartUpdate,
    CartPartialUpdate,
    CartItemCreate,
)
from .exceptions import Errors
from .validators import ValidRelationsInspector


if TYPE_CHECKING:
    from src.core.models import (
        Cart,
        User,
    )
    from .filters import CartFilter

CLASS = "Cart"
_CLASS = "cart"


class CartsService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
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
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        repository: CartsRepository = CartsRepository(
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
            id: int,
            to_schema: bool = True
    ):
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
        # product_orm = result["product_orm"] if "product_orm" in result else None

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
            user_id: int,
            to_schema: bool = False,
            maximized: bool = False,
    ):
        self.logger.info('Getting %r bound with user_id=%s from database' % (CLASS, user_id))
        sa_orm_model = await self.get_one_complex(
            id=user_id,
            to_schema=False
        )
        if isinstance(sa_orm_model, ORJSONResponse):
            self.logger.info('No %r bound with user_id=%s in database' % (CLASS, user_id))
            self.logger.info('Creating %r bound with user_id=%s in database' % (CLASS, user_id))
            sa_orm_model = await self.create_one(
                id=user_id,
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
            cart: Optional["Cart"] = None,
            to_schema: bool = False,
            maximized: bool = False,
    ):
        if not cart:
            cart: "Cart" = await self.get_or_create(
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
            cart: "Cart",
            product_id: int,
            to_schema: bool = False
    ):
        if hasattr(cart, "cart_items") and isinstance(cart.cart_items, Iterable):
            for cart_item in cart.cart_items:
                if cart_item.product_id == product_id:
                    return cart_item
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
            cart: "Cart",
            product_id: int,
            quantity: int = 1,
            to_schema: bool = True
    ):
        repository: CartsRepository = CartsRepository(
            session=self.session
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

        try:
            await repository.create_one_empty_item(orm_model=orm_model)
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
            cart: Optional["Cart"] = None,
            user_id: Optional[int] = None,
            to_schema: bool = False
    ):
        if not cart:
            cart: "Cart" = await self.get_or_create(
                user_id=user_id
            )
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
