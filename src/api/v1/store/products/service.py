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
from ..brands.repository import BrandsRepository
from ..rubrics.repository import RubricsRepository
from ..utils.image_utils import save_image

if TYPE_CHECKING:
    from src.core.models import (
        Product,
        Brand,
        Rubric,
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
            await utils.get_short_schema_from_orm(returned_orm_model)
        return returned_orm_model

    async def get_one_complex(
            self,
            id: int = None,
            slug: str = None,
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

        return await utils.get_schema_from_orm(returned_orm_model)

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

        # Expecting if rubric_ids format valid
        try:
            rubric_ids = await utils.temporary_fragment(ids=rubric_ids)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
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

        # Expecting if chosen brand_id existing
        try:
            brand_repository: BrandsRepository = BrandsRepository(
                session=self.session
            )
            brand_orm: "Brand" = await brand_repository.get_one(id=brand_id)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

        # Expecting if chosen rubric_ids existing
        try:
            rubric_repository: RubricsRepository = RubricsRepository(
                session=self.session
            )
            rubric_orms = []
            for rubric_id in rubric_ids:
                rubric_orm: "Rubric" = await rubric_repository.get_one(id=rubric_id)
                rubric_orms.append(rubric_orm)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

        # Creating empty model in database (with relations)
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
        for image_number, image_schema in enumerate(image_schemas):
            try:
                file_path: str = await save_image(
                    name=str(image_number+1),
                    image_object=image_schema,
                    path=f"media/{_CLASS}s",
                    folder=f"{orm_model.id}",
                    cleaning=False,
                )
            except Exception as exc:
                self.logger.error("Error wile writing file", exc_info=exc)
                await repository.delete_one(
                    orm_model=orm_model
                )
                return ORJSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "message": Errors.HANDLER_MESSAGE,
                        "detail": Errors.IMAGE_SAVING_ERROR,
                    }
                )

            self.logger.info("Image %r was successfully written" % image_schema)

            try:
                await repository.create_product_image(
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
