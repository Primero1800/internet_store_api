import logging
from fastapi import status
from typing import Sequence, TYPE_CHECKING, Union

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import AdditionalInformation, Product, ProductImage
from src.tools.exceptions import CustomException
from .exceptions import Errors

if TYPE_CHECKING:
    from .filters import (
        AddInfoFilter,
        AddInfoFilterComplex,
    )
    from .schemas import (
        AddInfoCreate,
        AddInfoUpdate,
        AddInfoPartialUpdate,
    )

CLASS = "AdditionalInformation"


class AddInfoRepository:
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
        orm_model = await self.session.get(AdditionalInformation, product_id)
        if not orm_model:
            text_error = f"product_id={product_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_one_complex(
            self,
            product_id: int = None,
    ):
        stmt_filter = select(AdditionalInformation).where(AdditionalInformation.product_id == product_id)
        stmt = stmt_filter.options(
            joinedload(AdditionalInformation.product).joinedload(Product.images),
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

        stmt = stmt_filtered.order_by(AdditionalInformation.product_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_all_full(
            self,
            filter_model: "AddInfoFilterComplex",
    ) -> Sequence:

        query_filter = filter_model.filter(
            select(AdditionalInformation).options(
                joinedload(AdditionalInformation.product).joinedload(Product.images)
            )
        )
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.order_by(AdditionalInformation.product_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["AddInfoCreate", "AddInfoUpdate", "AddInfoPartialUpdate"]
    ):
        orm_model: AdditionalInformation = AdditionalInformation(**instance.model_dump())
        return orm_model

    async def create_one(
            self,
            orm_model: AdditionalInformation
    ):
        try:
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%s %r was successfully created" % (CLASS, orm_model))
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                msg=Errors.ALREADY_EXISTS
            )

    async def delete_one(
            self,
            orm_model: AdditionalInformation,
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
