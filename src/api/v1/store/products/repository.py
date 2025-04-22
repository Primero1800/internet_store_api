import logging
from fastapi import status
from typing import Sequence, TYPE_CHECKING, Union, Optional

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
            maximized: bool = True,
            relations: list = []
    ):
        stmt_select = select(Product)
        if id:
            stmt_filter = stmt_select.where(Product.id == id)
        else:
            stmt_filter = stmt_select.where(Product.slug == slug)

        options_list = [
            joinedload(Product.images),
            joinedload(Product.brand).joinedload(Brand.image),
            joinedload(Product.rubrics).joinedload(Rubric.image),
        ]

        if maximized or "add_info" in relations:
            options_list.append(joinedload(Product.add_info))

        if maximized or "sale_info" in relations:
            options_list.append(joinedload(Product.sale_info))

        if maximized or "votes" in relations:
            options_list.append(joinedload(Product.votes))

        stmt = stmt_filter.options(*options_list)

        result: Result = await self.session.execute(stmt)
        orm_model: Product | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"id={id}" if id else f"slug={slug!r}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_one_complex_full(
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
        )

        result: Result = await self.session.execute(stmt)
        orm_model: Product | None = result.unique().scalar_one_or_none()

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
            self.logger.info("%s %r was successfully created" % (CLASS, orm_model))
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

    async def edit_one_with_relations(
            self,
            instance:  Union["ProductUpdate", "ProductPartialUpdate"],
            orm_model: Product,
            rubric_orms: Optional[list[Rubric]] = None,
            image_schemas: Optional[list[str]] = None,
            is_partial: bool = False
    ):
        if is_partial:
            instance.start_price = instance.start_price or orm_model.start_price
            instance.discount = instance.discount if isinstance(instance.discount, int) else orm_model.discount
        for key, val in instance.model_dump(
                exclude_unset=is_partial,
                exclude_none=is_partial,
        ).items():
            setattr(orm_model, key, val)

        self.logger.warning(f"Editing %r in database" % orm_model)
        try:

            if rubric_orms:
                orm_model.rubrics.clear()
                for rubric_orm_model in rubric_orms:
                    orm_model.rubrics.append(rubric_orm_model)

            if image_schemas:
                for old_image in orm_model.images:
                    await self.session.delete(old_image)

            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%r %r was successfully edited" % (CLASS, orm_model))
            self.logger.info("Rubrics list was successfully edited")
        except IntegrityError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                msg=Errors.already_exists_titled(instance.title)
            )
