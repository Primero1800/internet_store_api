import logging
from typing import Sequence, Union, TYPE_CHECKING

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import Rubric, Product, RubricImage
from src.tools.exceptions import CustomException
from .exceptions import Errors

if TYPE_CHECKING:
    from .schemas import (
        RubricCreate,
        RubricUpdate,
        RubricPartialUpdate,
    )


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

    async def get_one(
            self,
            id: int
    ):
        orm_model = await self.session.get(Rubric, id)
        if not orm_model:
            text_error = f"id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all_full(self) -> Sequence:
        stmt = select(Rubric).options(
            joinedload(Rubric.image),
            joinedload(Rubric.products).joinedload(Product.images),
        ).order_by(Rubric.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["RubricCreate", "RubricUpdate", "RubricPartialUpdate"]
    ):
        orm_model: Rubric = Rubric(**instance.model_dump())
        return orm_model

    async def create_one_empty(
            self,
            orm_model: Rubric
    ):
        try:
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%r %r was successfully created" % (CLASS, orm_model))
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                msg=Errors.already_exists_titled(orm_model.title)
            )

    async def create_rubric_image(
            self,
            file: str,
            orm_model: Rubric
    ):
        try:
            image: RubricImage | None = RubricImage(file=file, brand_id=orm_model.id)
            self.session.add(image)
            await self.session.commit()
            self.logger.info("%sImage %r was successfully created" % (CLASS, image))
        except IntegrityError as error:
            self.logger.error(
                "Error occured while saving data to database. Parent model will be deleted", exc_info=error
            )
            await self.delete_one(
                orm_model=orm_model,
            )
            raise CustomException(
                msg=f"Error while {image!r} creating."
            )

    async def delete_one(
            self,
            orm_model: Rubric,
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