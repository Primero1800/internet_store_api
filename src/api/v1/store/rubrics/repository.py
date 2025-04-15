import logging
from typing import Sequence

from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import Rubric, Product
from src.tools.exceptions import CustomException


CLASS = "Rubric"


class RubricsRepository:
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
        stmt_select = select(Rubric)
        if id:
            stmt_filter = stmt_select.where(Rubric.id == id)
        else:
            stmt_filter = stmt_select.where(Rubric.slug == slug)

        stmt = stmt_filter.options(
            joinedload(Rubric.image),
            joinedload(Rubric.products).joinedload(Product.images),
        ).order_by(Rubric.id)

        result: Result = await self.session.execute(stmt)
        orm_model: Rubric | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"id={id}" if id else f"slug={slug!r}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all(self) -> Sequence:
        stmt = select(Rubric).options(
            joinedload(Rubric.image)
        ).order_by(Rubric.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()