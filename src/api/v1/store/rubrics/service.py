import logging

from sqlalchemy.ext.asyncio import AsyncSession

from . import utils
from .repository import RubricsRepository


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
