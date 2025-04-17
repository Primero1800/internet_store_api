import logging
from decimal import Decimal
from typing import TYPE_CHECKING

from fastapi import UploadFile, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.discount_choices import DiscountChoices
from src.tools.exceptions import CustomException
from . import utils
from .repository import ProductsRepository
from .schemas import (
    ProductCreate,
    ProductUpdate,
    ProductPartialUpdate,
)
from .exceptions import Errors
from .validators import ValidRelationsInspector
from ..utils.image_utils import save_image, del_directory

if TYPE_CHECKING:
    from src.core.models import (
        Product,
    )
    from .filters import ProductFilter

CLASS = "Product"
_CLASS = "product"


class ProductsService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.repository = None

    async def get_all(
            self,
            filter_model: "ProductFilter",
    ):
        repository: ProductsRepository = ProductsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "ProductFilter"
    ):
        repository: ProductsRepository = ProductsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all_full(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        return result

    async def get_one(
            self,
            id: int,
            to_schema: bool = True
    ):
        repository: ProductsRepository = ProductsRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one(
                id=id,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        if to_schema:
            return await utils.get_short_schema_from_orm(returned_orm_model)
        return returned_orm_model

    async def get_one_complex(
            self,
            id: int = None,
            slug: str = None,
            to_schema: bool = True,
    ):
        repository: ProductsRepository = ProductsRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one_complex(
                id=id,
                slug=slug,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        if to_schema:
            return await utils.get_schema_from_orm(returned_orm_model)
        return returned_orm_model

    async def create_one(
            self,
            title: str,
            description: str,
            brand_id: int,
            start_price: Decimal,
            available: bool,
            discount: DiscountChoices,
            quantity: int,
            rubric_ids: str | list,
            image_schemas: list[UploadFile],
    ):
        repository: ProductsRepository = ProductsRepository(
            session=self.session
        )
        self.repository = repository

        # Expecting if ProductCreate data valid
                # catching ValidationError in exception_handler
        instance: ProductCreate = ProductCreate(
            title=title,
            description=description,
            brand_id=brand_id,
            start_price=start_price,
            available=available,
            discount=discount,
            quantity=quantity
        )
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

        inspector = ValidRelationsInspector(
            session=self.session,
            **{"rubric_ids": rubric_ids, "brand_id": brand_id}
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result
        rubric_orms = result["rubric_orms"] if "rubric_orms" in result else None

        # Creating model in database (with relations)
        try:
            await repository.create_one_with_relations(
                orm_model=orm_model,
                rubric_orm_models=rubric_orms
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

        # Working with images. If exception -.> delete created model
        for image_number, image_schema in enumerate(image_schemas, 1):
            # Saving image to file
            file_path = await self.saving_image_from_schema_with_rollback(
                image_schema=image_schema, image_number=image_number, orm_model=orm_model
            )
            if isinstance(file_path, ORJSONResponse):
                return file_path
            self.logger.info("Image %r was successfully written as '%s.*'" % (image_schema.filename, image_number))

            # Saving image_path to database as ProductImage
            result = await self.saving_image_to_db(orm_model=orm_model, file_path=file_path)
            if isinstance(result, ORJSONResponse):
                return result

        self.logger.info("Product %r was successfully created" % orm_model)

        return await self.get_one_complex(
            id=orm_model.id
        )

    async def delete_one(
            self,
            orm_model: "Product",
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: ProductsRepository = ProductsRepository(
            session=self.session
        )
        try:
            return await repository.delete_one(orm_model=orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

    async def edit_one(
            self,
            title: str,
            description: str,
            brand_id: int,
            start_price: Decimal,
            available: bool,
            discount: DiscountChoices,
            quantity: int,
            rubric_ids: str | list,
            image_schemas: list,
            orm_model: "Product",
            is_partial: bool = False
    ):
        repository: ProductsRepository = ProductsRepository(
            session=self.session,
        )
        self.repository = repository

        # catching ValidationError in exception_handler
        updating_dictionary = {
            "title": title,
            "description": description,
            "brand_id": brand_id,
            "start_price": start_price,
            "available": available,
            "discount": discount,
            "quantity": quantity,
        }
        if is_partial:
            instance: ProductPartialUpdate = ProductPartialUpdate(**updating_dictionary)
        else:
            instance: ProductUpdate = ProductUpdate(**updating_dictionary)

        inspector = ValidRelationsInspector(
            session=self.session,
            **{"rubric_ids": rubric_ids, "brand_id": brand_id}
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result
        rubric_orms = result["rubric_orms"] if "rubric_orms" in result else None

        # Working with images. If exception -.> stop editing model
        if image_schemas:
            await del_directory(
                path=f"media/{_CLASS}s",
                folder=f"{orm_model.id}",
            )
            for image_number, image_schema in enumerate(image_schemas, 1):
                # Saving image to file
                file_path = await self.saving_image_from_schema_with_rollback(
                    image_schema=image_schema, image_number=image_number, orm_model=orm_model
                )
                if isinstance(file_path, ORJSONResponse):
                    return file_path
                self.logger.info("Image %r was successfully written as '%s.*'" % (image_schema.filename, image_number))

                # Saving image_path to database as ProductImage
                result = await self.saving_image_to_db(orm_model=orm_model, file_path=file_path)
                if isinstance(result, ORJSONResponse):
                    return result

        # Editing model in database (with relations)
        try:
            await repository.edit_one_with_relations(
                instance=instance,
                orm_model=orm_model,
                rubric_orms=rubric_orms,
                image_schemas=image_schemas,
                is_partial=is_partial,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

        self.logger.info("Product %r was successfully edited" % orm_model)

        return await self.get_one_complex(
            id=orm_model.id
        )

    async def saving_image_from_schema_with_rollback(
            self,
            image_schema: UploadFile,
            image_number: int,
            orm_model: "Product"
    ):
        try:
            file_path: str = await save_image(
                name=str(image_number),
                image_object=image_schema,
                path=f"media/{_CLASS}s",
                folder=f"{orm_model.id}",
                cleaning=False,
            )
            return file_path
        except Exception as exc:
            self.logger.error("Error wile writing file", exc_info=exc)
            await self.repository.delete_one(
                orm_model=orm_model
            )
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.IMAGE_SAVING_ERROR,
                }
            )

    async def saving_image_to_db(
            self,
            orm_model: "Product",
            file_path: str
    ):
        try:
            await self.repository.create_product_image(
                file=file_path,
                orm_model=orm_model
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
