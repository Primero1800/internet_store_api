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
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg=Errors.DATABASE_ERROR()
            )
