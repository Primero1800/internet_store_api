import logging
from fastapi import status
from typing import Sequence, TYPE_CHECKING, Union, Optional

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import Order, User, Product, ProductImage
from src.tools.exceptions import CustomException
from .exceptions import Errors

if TYPE_CHECKING:
    from .schemas import (
        OrderCreate,
        OrderUpdate,
        OrderPartialUpdate,
    )
    from .filters import OrderFilter


CLASS = "Order"


class OrdersRepository:
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
        stmt_filter = select(Order).where(Order.id == id)

        options_list = []

        if maximized or "user" in relations:
            options_list.append(joinedload(Order.user))

        stmt = stmt_filter.options(*options_list)

        result: Result = await self.session.execute(stmt)
        orm_model: Order | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_one(
            self,
            id: int
    ):
        orm_model = await self.session.get(Order, id)
        if not orm_model:
            text_error = f"id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all(
            self,
            filter_model: "OrderFilter",
            user_id: Optional[int] = None,
    ) -> Sequence:

        start_query = select(Order).where(Order.user_id == user_id) if user_id else select(Order)

        query_filter = filter_model.filter(start_query)
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.order_by(Order.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_all_full(
            self,
            filter_model: "OrderFilter",
            user_id: Optional[int] = None,
    ) -> Sequence:

        start_query = select(Order).where(Order.user_id == user_id) if user_id else select(Order)

        query_filter = filter_model.filter(start_query)
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
            joinedload(Order.user),
        ).order_by(Order.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["OrderCreate", "OrderUpdate", "OrderPartialUpdate"]
    ):
        orm_model: Order = Order(**instance.model_dump())
        return orm_model

    async def create_one(
            self,
            orm_model: Order,
    ):
        try:
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%s %r was successfully created" % (CLASS, orm_model))
            return orm_model
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg=Errors.DATABASE_ERROR()
            )
