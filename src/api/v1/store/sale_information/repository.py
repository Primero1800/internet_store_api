import logging
from typing import Sequence, TYPE_CHECKING, Union

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import SaleInformation, Product, ProductImage
from src.tools.exceptions import CustomException
from .exceptions import Errors

if TYPE_CHECKING:
    from .filters import (
        SaleInfoFilter,
        SaleInfoFilterComplex,
    )
    from .schemas import (
        SaleInfoCreate,
        SaleInfoUpdate,
        SaleInfoPartialUpdate,
    )

CLASS = "SaleInformation"


class SaleInfoRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_one(
            self,
            product_id: int
    ):
        orm_model = await self.session.get(SaleInformation, product_id)
        if not orm_model:
            text_error = f"product_id={product_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_one_complex(
            self,
            product_id: int = None,
            maximized: bool = True,
            relations: list = []
    ):
        stmt = select(SaleInformation).where(SaleInformation.product_id == product_id)
        if maximized or "product" in relations:
            stmt = stmt.options(
                joinedload(SaleInformation.product).joinedload(Product.images),
            )
        result: Result = await self.session.execute(stmt)
        orm_model: SaleInformation | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"product_id={product_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all(
            self,
            filter_model: "SaleInfoFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(SaleInformation))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.order_by(SaleInformation.product_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_all_full(
            self,
            filter_model: "SaleInfoFilterComplex",
    ) -> Sequence:

        query_filter = filter_model.filter(
            select(SaleInformation).options(
                joinedload(SaleInformation.product).joinedload(Product.images)
            )
        )
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.order_by(SaleInformation.product_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["SaleInfoCreate", "SaleInfoUpdate", "SaleInfoPartialUpdate"]
    ):
        orm_model: SaleInformation = SaleInformation(**instance.model_dump())
        return orm_model
