import logging
from fastapi import status
from typing import Sequence, TYPE_CHECKING, Union

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import Cart, CartItem, Product
from src.tools.exceptions import CustomException
from .exceptions import Errors

if TYPE_CHECKING:
    from .schemas import (
        CartCreate,
        CartUpdate,
        CartPartialUpdate,
        CartItemCreate,
        CartItemUpdate,
    )
    from .filters import CartFilter


CLASS = "Cart"


class CartsRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_one_complex(
            self,
            id: int = None,
            maximized: bool = True,
            relations: list = []
    ):
        stmt_filter = select(Cart).where(Cart.user_id == id)

        options_list = []

        if maximized or "products" in relations:
            options_list.append(joinedload(Cart.cart_items).joinedload(CartItem.product).joinedload(Product.images))

        if maximized or "user" in relations:
            options_list.append(joinedload(Cart.user))

        stmt = stmt_filter.options(*options_list)

        result: Result = await self.session.execute(stmt)
        orm_model: Cart | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"user_id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_one(
            self,
            id: int
    ):
        stmt = select(Cart).where(Cart.user_id == id).options(
            joinedload(Cart.cart_items)
        )

        result: Result = await self.session.execute(stmt)
        orm_model: Cart | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"user_id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all(
            self,
            filter_model: "CartFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(Cart))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
            joinedload(Cart.cart_items)
        ).order_by(Cart.user_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_all_full(
            self,
            filter_model: "CartFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(Cart))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
            joinedload(Cart.cart_items).joinedload(CartItem.product).joinedload(Product.images),
            joinedload(Cart.user),
        ).order_by(Cart.user_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["CartCreate", "CartUpdate", "CartPartialUpdate"]
    ):
        orm_model: Cart = Cart(**instance.model_dump())
        return orm_model

    async def create_one_empty(
            self,
            orm_model: Cart
    ):
        try:
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%s %r was successfully created" % (CLASS, orm_model))
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                msg=Errors.already_exists_id(user_id=orm_model.user_id)
            )

    async def delete_one(
            self,
            orm_model: Cart,
    ) -> None:
        try:
            self.logger.info(f"Deleting %r from database" % orm_model)
            await self.session.delete(orm_model)
            await self.session.commit()
        except IntegrityError as exc:
            self.logger.error("Error while deleting data from database", exc_info=exc)
            raise CustomException(
                msg="Error while deleting %r from database" % orm_model
            )

    async def edit_one_empty(
            self,
            instance:  Union["CartUpdate", "CartPartialUpdate"],
            orm_model: Cart,
            is_partial: bool = False
    ):
        for key, val in instance.model_dump(
                exclude_unset=is_partial,
                exclude_none=is_partial,
        ).items():
            setattr(orm_model, key, val)

        self.logger.warning(f"Editing %r in database" % orm_model)
        try:
            await self.session.commit()
            await self.session.refresh(orm_model)
        except IntegrityError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                msg=Errors.already_exists_id(instance.user_id)
            )

    async def get_one_item_complex(
            self,
            cart_id: int,
            product_id: int,
            maximized: bool = True,
    ):
        stmt_filter = select(CartItem).where(CartItem.cart_id == cart_id).where(CartItem.product_id == product_id)

        options_list = []
        if maximized:
            options_list.append(joinedload(CartItem.product).joinedload(Product.images))
        stmt = stmt_filter.options(*options_list)

        result: Result = await self.session.execute(stmt)
        orm_model: Cart | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"cart_id={cart_id} and product_id={product_id}"
            raise CustomException(
                msg=f"{CLASS}Item with {text_error} not found"
            )
        return orm_model

    async def get_item_orm_model_from_schema(
            self,
            instance: Union["CartItemCreate", "CartItemUpdate"]
    ):
        orm_model: CartItem = CartItem(**instance.model_dump())
        return orm_model

    async def create_one_empty_item(
            self,
            orm_model: CartItem
    ):
        try:
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%sItem %r was successfully created" % (CLASS, orm_model))
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                msg=Errors.item_already_exists_id(cart_id=orm_model.cart_id, product_id=orm_model.product_id)
            )

    async def clear_cart(
            self,
            cart: Cart,
    ):
        try:
            for item in cart.cart_items:
                await self.session.delete(item)
            await self.session.commit()
            await self.session.refresh(cart)
        except IntegrityError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg=Errors.DATABASE_ERROR
            )
        return cart
