import logging
from typing import TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from .repository import AddInfoRepository
from .exceptions import Errors
from . import utils

if TYPE_CHECKING:
    from .filters import AddInfoFilter, AddInfoFilterComplex

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
        # TODO KeyError
        listed_orm_models = await repository.get_all_full(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        return result

    async def get_one_complex(
            self,
            id: int = None,
            product_id: int = None,
            to_schema: bool = True,
    ):
        repository: AddInfoRepository = AddInfoRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one_complex(
                id=id,
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
            return await utils.get_schema_from_orm(returned_orm_model)
        return returned_orm_model
