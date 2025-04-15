import logging
from typing import TYPE_CHECKING

from fastapi import UploadFile, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import ProductsRepository
from .schemas import (
    ProductCreate,
    ProductUpdate,
    ProductPartialUpdate,
)
from .exceptions import Errors
from ..utils.image_utils import save_image

if TYPE_CHECKING:
    from src.core.models import Product
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

