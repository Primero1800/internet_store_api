from typing import TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException

from .exceptions import Errors
from ..rubrics.repository import RubricsRepository
from ..brands.repository import BrandsRepository
from . import utils

if TYPE_CHECKING:
    from src.core.models import (
        Rubric,
        Brand,
    )


class ValidRelationsException(Exception):
    pass


class ValidRelationsInspector:
    def __init__(self, session: AsyncSession, **kwargs):
        self.session = session
        self.need_inspect = []
        self.result = {}
        self.error = None

        if "rubric_ids" in kwargs:
            self.need_inspect.append(("rubric_ids", kwargs["rubric_ids"]))
        if "brand_id" in kwargs:
            self.need_inspect.append(("brand_id", kwargs["brand_id"]))

    async def inspect(self):
        while self.need_inspect:
            to_inspect, params = self.need_inspect.pop(0)
            try:
                if to_inspect == "rubric_ids":
                    await self.expecting_rubric_ids(rubric_ids=params)
                    await self.expecting_rubrics_exist(rubric_ids=self.result['rubric_ids'])
                if to_inspect == "brand_id":
                    await self.expecting_brand_exists(brand_id=params)
            except ValidRelationsException:
                return self.error
        return self.result

    async def expecting_rubric_ids(self, rubric_ids: str | list):
        # Expecting if rubric_ids format valid
        try:
            self.result['rubric_ids'] = await utils.temporary_fragment(ids=rubric_ids)
        except CustomException as exc:
            self.error = ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
            raise ValidRelationsException()

    async def expecting_rubrics_exist(self, rubric_ids: list):
        # Expecting if chosen rubric_ids are existing
        try:
            rubric_repository: RubricsRepository = RubricsRepository(
                session=self.session
            )
            rubric_orms = []
            for rubric_id in rubric_ids:
                rubric_orm: "Rubric" = await rubric_repository.get_one(id=rubric_id)
                rubric_orms.append(rubric_orm)
            self.result['rubric_orms'] =rubric_orms
        except CustomException as exc:
            self.error = ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
            raise ValidRelationsException

    async def expecting_brand_exists(self, brand_id: int):
        # Expecting if chosen brand_id existing
        try:
            brand_repository: BrandsRepository = BrandsRepository(
                session=self.session
            )
            brand_orm: "Brand" = await brand_repository.get_one(id=brand_id)
            self.result['brand_orm'] = brand_orm
        except CustomException as exc:
            self.error = ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
            raise ValidRelationsException
