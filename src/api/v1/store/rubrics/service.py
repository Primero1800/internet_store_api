import logging

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import RubricsRepository
from .exceptions import Errors


class RubricsService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all(self):
        repository: RubricsRepository = RubricsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all()
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(self):
        repository: RubricsRepository = RubricsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all_full()
        for orm_model in listed_orm_models:
            result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        return result

    async def get_one_complex(
            self,
            id: int = None,
            slug: str = None,
    ):
        repository: RubricsRepository = RubricsRepository(
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
