import logging
from typing import Sequence, TYPE_CHECKING

from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import AdditionalInformation
from src.tools.exceptions import CustomException

if TYPE_CHECKING:
    from .filters import (
        AddInfoFilter,
        AddInfoFilterComplex,
    )

CLASS = "AdditionalInformation"


class AddInfoRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_one_complex(
            self,
            id: int = None,
            product_id: int = None,
            slug: str = None,
    ):
        stmt_select = select(AdditionalInformation)
        if id:
            stmt_filter = stmt_select.where(AdditionalInformation.id == id)
        else:
            stmt_filter = stmt_select.where(AdditionalInformation.product_id == product_id)

        stmt = stmt_select.options(
            joinedload(AdditionalInformation.product),
        )

        result: Result = await self.session.execute(stmt)
        orm_model: AdditionalInformation | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"id={id}" if id else f"product_id={product_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all(
            self,
            filter_model: "AddInfoFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(AdditionalInformation))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
        ).order_by(AdditionalInformation.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_all_full(
            self,
            filter_model: "AddInfoFilterComplex",
    ) -> Sequence:

        query_filter = filter_model.filter(
            select(AdditionalInformation).options(
                joinedload(AdditionalInformation.product)
            )
        )
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.order_by(AdditionalInformation.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()
