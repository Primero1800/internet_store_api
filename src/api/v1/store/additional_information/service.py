import logging
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import AddInfoRepository
from . import utils

if TYPE_CHECKING:
    from .filters import AddInfoFilter

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
