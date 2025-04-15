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

    async def get_one_complex(
            self,
            id: int = None,
            slug: str = None,
    ):
        stmt_select = select(Product)
        if id:
            stmt_filter = stmt_select.where(Product.id == id)
        else:
            stmt_filter = stmt_select.where(Product.slug == slug)

        stmt = stmt_filter.options(
            joinedload(Product.images),
            joinedload(Product.brand).joinedload(Brand.image),
            joinedload(Product.rubrics).joinedload(Rubric.image),
        ).order_by(Product.id)

        result: Result = await self.session.execute(stmt)
        orm_model: Brand | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"id={id}" if id else f"slug={slug!r}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

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

    async def get_all_full(
            self,
            filter_model: "ProductFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(Product))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
            joinedload(Product.images),
            joinedload(Product.brand).joinedload(Brand.image),
            joinedload(Product.rubrics).joinedload(Rubric.image),
        ).order_by(Product.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["ProductCreate", "ProductUpdate", "ProductPartialUpdate"]
    ):
        orm_model: Product = Product(**instance.model_dump())
        return orm_model
