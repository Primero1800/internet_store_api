import logging
from typing import Sequence, TYPE_CHECKING, Union

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import Product, ProductImage, Brand, Rubric
from src.tools.exceptions import CustomException
from .exceptions import Errors

if TYPE_CHECKING:
    from .schemas import (
        ProductCreate,
        ProductUpdate,
        ProductPartialUpdate,
    )
    from .filters import ProductFilter


CLASS = "Product"


class ProductsRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_one(
            self,
            id: int
    ):
        orm_model = await self.session.get(Product, id)
        if not orm_model:
            text_error = f"id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all(
            self,
            filter_model: "ProductFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(Product))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
            joinedload(Product.images)
        ).order_by(Product.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()
