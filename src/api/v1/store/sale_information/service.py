import logging
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from .repository import SaleInfoRepository
from .exceptions import Errors
from .validators import ValidRelationsInspector
from .schemas import (
    SaleInfoCreate,
    SaleInfoUpdate,
    SaleInfoPartialUpdate,
)
from . import utils

if TYPE_CHECKING:
    from .filters import SaleInfoFilter, SaleInfoFilterComplex
    from src.core.models import (
        SaleInformation,
    )

CLASS = "SaleInformation"
_CLASS = "sale_info"


class SaleInfoService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.repository = None

    async def get_all(
            self,
            filter_model: "SaleInfoFilter",
    ):
        repository: SaleInfoRepository = SaleInfoRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "SaleInfoFilterComplex"
    ):
        repository: SaleInfoRepository = SaleInfoRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all_full(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        return result

    async def get_one(
            self,
            product_id: int = None,
            to_schema: bool = True,
    ):
        repository: SaleInfoRepository = SaleInfoRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one(
                product_id=product_id,
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
            product_id: int = None,
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        repository: SaleInfoRepository = SaleInfoRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one_complex(
                product_id=product_id,
                maximized=maximized,
                relations=relations,
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
            return await utils.get_schema_from_orm(
                orm_model=returned_orm_model,
                maximized=maximized,
                relations=relations,
            )
        return returned_orm_model
