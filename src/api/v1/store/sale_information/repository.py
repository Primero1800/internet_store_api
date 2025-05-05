import logging
from typing import Sequence, TYPE_CHECKING, Union

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import SaleInformation, Product
from src.tools.exceptions import CustomException, UnreachableValueError
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

        query_filter = filter_model.filter(select(SaleInformation).outerjoin(Product))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
            joinedload(SaleInformation.product).joinedload(Product.images)
        ).order_by(SaleInformation.product_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["SaleInfoCreate", "SaleInfoUpdate", "SaleInfoPartialUpdate"]
    ):
        orm_model: SaleInformation = SaleInformation(**instance.model_dump())
        return orm_model

    async def create_one(
            self,
            orm_model: SaleInformation
    ):
        try:
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%s %r was successfully created" % (CLASS, orm_model))
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                msg=Errors.ALREADY_EXISTS()
            )

    async def delete_one(
            self,
            orm_model: SaleInformation,
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

    async def edit_one(
            self,
            instance:  Union["SaleInfoUpdate", "SaleInfoPartialUpdate"],
            orm_model: SaleInformation,
            is_partial: bool = False
    ):
        if is_partial:
            instance.rating_summary = instance.rating_summary if isinstance(instance.rating_summary, int) \
                else orm_model.rating_summary
            instance.voted_count = instance.voted_count if isinstance(instance.voted_count, int) \
                else orm_model.voted_count
        try:
            for key, val in instance.model_dump(
                    exclude_unset=is_partial,
                    exclude_none=is_partial,
            ).items():
                setattr(orm_model, key, val)
        except ZeroDivisionError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                msg="Division by zero: voted_count=0"
            )
        except UnreachableValueError as exc:
            self.logger.error("Error occurred while editing data in database. Rating can't be more than 5")
            raise CustomException(
                msg="Rating must be not more than 5"
            )

        self.logger.warning(f"Editing %r in database" % orm_model)
        try:
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%r %r was successfully edited" % (CLASS, orm_model))
        except IntegrityError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                msg=Errors.already_exists_product_id(instance.product_id)
            )
