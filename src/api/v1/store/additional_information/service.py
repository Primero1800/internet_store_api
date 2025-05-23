import logging
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from .repository import AddInfoRepository
from .exceptions import Errors
from .validators import ValidRelationsInspector
from .schemas import (
    AddInfoCreate,
    AddInfoUpdate,
    AddInfoPartialUpdate,
)
from . import utils

if TYPE_CHECKING:
    from .filters import AddInfoFilter, AddInfoFilterComplex
    from src.core.models import (
        AdditionalInformation,
    )

CLASS = "AdditionalInformation"
_CLASS = "add_info"


class AddInfoService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.repository = None

    async def get_all(
            self,
            filter_model: "AddInfoFilter",
    ):
        repository: AddInfoRepository = AddInfoRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "AddInfoFilterComplex"
    ):
        repository: AddInfoRepository = AddInfoRepository(
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
        repository: AddInfoRepository = AddInfoRepository(
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
                    "message": Errors.HANDLER_MESSAGE(),
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
            relations: list | None = None,
            to_schema: bool = True,
    ):
        repository: AddInfoRepository = AddInfoRepository(
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
                    "message": Errors.HANDLER_MESSAGE(),
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

    async def create_one(
            self,
            product_id: int,
            weight: Optional[Decimal],
            size: Optional[str],
            guarantee: Optional[str],
    ):
        repository: AddInfoRepository = AddInfoRepository(
            session=self.session
        )
        self.repository = repository

        # Expecting if ProductCreate data valid
                # catching ValidationError in exception_handler
        instance: AddInfoCreate = AddInfoCreate(
            product_id=product_id,
            weight=weight,
            size=size,
            guarantee=guarantee,
        )
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

        inspector = ValidRelationsInspector(
            session=self.session,
            **{"product_id": product_id}
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result

        try:
            await repository.create_one(
                orm_model=orm_model,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        self.logger.info("AdditionalInformation for Product id=%s was successfully created" % orm_model.product_id)

        return await self.get_one_complex(
            product_id=orm_model.product_id
        )

    async def delete_one(
            self,
            orm_model: "AdditionalInformation",
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: AddInfoRepository = AddInfoRepository(
            session=self.session
        )
        try:
            return await repository.delete_one(orm_model=orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

    async def edit_one(
            self,
            product_id: int,
            orm_model: "AdditionalInformation",
            weight: Optional[Decimal],
            size: Optional[str],
            guarantee: Optional[str],
            is_partial: bool = False
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: AddInfoRepository = AddInfoRepository(
            session=self.session
        )
        self.repository = repository

        # Expecting if Update or PartialUpdate data valid
                # catching ValidationError in exception_handler
        updating_dictionary = {
            "product_id": product_id,
            "weight": weight,
            "size": size,
            "guarantee": guarantee,
        }
        if is_partial:
            instance: AddInfoPartialUpdate = AddInfoPartialUpdate(**updating_dictionary)
        else:
            instance: AddInfoUpdate = AddInfoUpdate(**updating_dictionary)

        inspector = ValidRelationsInspector(
            session=self.session,
            **{"product_id": product_id}
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result

        try:
            await repository.edit_one(
                orm_model=orm_model,
                instance=instance,
                is_partial=is_partial,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        self.logger.info("AdditionalInformation for Product id=%s was successfully edited" % orm_model.product_id)

        return await self.get_one_complex(
            product_id=orm_model.product_id
        )
