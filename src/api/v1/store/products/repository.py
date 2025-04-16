import logging
from fastapi import status
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
        print("OOOOOOOOORRRRRM MODEL DICT", orm_model.to_dict())
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

    async def create_one_empty(
            self,
            orm_model: Product
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

    async def create_one_with_relations(
            self,
            orm_model: Product,
            rubric_orm_models: list[Rubric]
    ):
        try:
            self.session.add(orm_model)
            for rubric_orm_model in rubric_orm_models:
                orm_model.rubrics.append(rubric_orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%r %r was successfully created" % (CLASS, orm_model))
            self.logger.info("Rubrics were successfully added to product")
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model with relations creating", exc_info=error)
            raise CustomException(
                msg=Errors.already_exists_titled(orm_model.title)
            )

    async def create_product_image(
            self,
            file: str,
            orm_model: Product
    ):
        try:
            image: ProductImage | None = ProductImage(file=file, product_id=orm_model.id)
            self.session.add(image)
            await self.session.commit()
            self.logger.info("%sImage %r was successfully created" % (CLASS, image))
        except IntegrityError as error:
            self.logger.error(
                "Error occurred while saving data to database. Parent model will be deleted", exc_info=error
            )
            await self.delete_one(
                orm_model=orm_model,
            )
            raise CustomException(
                msg=f"Error while {image!r} creating."
            )

    async def add_rubrics_to_model(
            self,
            orm_model: Product,
            rubric_orm_models: list[Rubric]
    ):
        try:
            for rubric_orm_model in rubric_orm_models:
                orm_model.rubrics.append(rubric_orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("Rubrics were successfully added to product")
        except IntegrityError as exc:
            self.logger.error(Errors.DATABASE_ERROR, exc_info=exc)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg=Errors.DATABASE_ERROR
            )

    async def delete_one(
            self,
            orm_model: Product,
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
