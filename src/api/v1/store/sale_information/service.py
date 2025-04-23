import logging
from typing import TYPE_CHECKING, Optional

from fastapi import status
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

    async def create_one(
            self,
            product_id: int,
            to_schema: Optional[bool] = True,
    ):
        repository: SaleInfoRepository = SaleInfoRepository(
            session=self.session
        )
        self.repository = repository

        # Expecting if ProductCreate data valid
                # catching ValidationError in exception_handler
        instance: SaleInfoCreate = SaleInfoCreate(
            product_id=product_id,
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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

        self.logger.info("%s for Product id=%s was successfully created" % (CLASS, orm_model.product_id))

        return await self.get_one_complex(
            product_id=orm_model.product_id,
            to_schema=to_schema,
        )

    async def delete_one(
            self,
            orm_model: "SaleInformation",
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: SaleInfoRepository = SaleInfoRepository(
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
            product_id: int,
            orm_model: "SaleInformation",
            viewed_count: Optional[int] = None,
            sold_count: Optional[int] = None,
            voted_count: Optional[int] = None,
            rating_summary: Optional[int] = None,
            is_partial: bool = False,
            to_schema: Optional[bool] = True
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: SaleInfoRepository = SaleInfoRepository(
            session=self.session
        )
        self.repository = repository

        # Expecting if Update or PartialUpdate data valid
        # catching ValidationError in exception_handler
        updating_dictionary = {
            "product_id": product_id,
            "viewed_count": viewed_count,
            "sold_count": sold_count,
            "voted_count": voted_count,
            "rating_summary": rating_summary,
        }
        if is_partial:
            instance: SaleInfoPartialUpdate = SaleInfoPartialUpdate(**updating_dictionary)
        else:
            instance: SaleInfoUpdate = SaleInfoUpdate(**updating_dictionary)

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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

        self.logger.info("AdditionalInformation for Product id=%s was successfully edited" % orm_model.product_id)

        return await self.get_one_complex(
            product_id=orm_model.product_id,
            to_schema=to_schema,
        )

    async def get_or_create(
            self,
            product_id: int
    ):
        self.logger.info('Getting %r bound with product_id=%s from database' % (CLASS, product_id))
        sa_orm_model = await self.get_one(
            product_id=product_id,
            to_schema=False
        )
        if isinstance(sa_orm_model, ORJSONResponse):
            self.logger.info('No %r bound with product_id=%s in database' % (CLASS, product_id))
            self.logger.info('Creating %r bound with product_id=%s in database' % (CLASS, product_id))
            sa_orm_model = await self.create_one(
                product_id=product_id,
                to_schema=False,
            )
        return sa_orm_model

    async def do_vote(
            self,
            product_id_vote_add: Optional[int] = None,
            vote_add: Optional[int] = None,
            product_id_vote_del: Optional[int] = None,
            vote_del: Optional[int] = None,
    ):
        if product_id_vote_add is None and product_id_vote_del is None:
            return []

        # CASE IF NO MORE VOTES, JUST EDIT OLD ONE
        if product_id_vote_add == product_id_vote_del:
            if vote_add is None or vote_del is None:
                return ORJSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "message": Errors.HANDLER_MESSAGE,
                        "detail": "Values 'votes' both must be valid integers",
                    }
                )
            delta = vote_add - vote_del
            if not delta:
                return []
            orm_model = await self.get_or_create(
                product_id=product_id_vote_add,
            )
            if isinstance(orm_model, ORJSONResponse):
                return orm_model
            orm_model = await self.edit_one(
                product_id=product_id_vote_add,
                is_partial=True,
                orm_model=orm_model,
                rating_summary=orm_model.rating_summary + delta,
            )
            if isinstance(orm_model, ORJSONResponse):
                return orm_model
            self.logger.info('Rating_summary was successfully edited')
            return [orm_model]

        orm_models = []

        if product_id_vote_add:
            if vote_add is None :
                self.logger.error("Error while changing rating: Value 'vote_add' must be valid integer")
                return ORJSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "message": Errors.HANDLER_MESSAGE,
                        "detail": "Value 'vote_add' must be valid integer",
                    }
                )
            orm_model = await self.get_or_create(
                product_id=product_id_vote_add,
            )
            if isinstance(orm_model, ORJSONResponse):
                return orm_model
            orm_model = await self.edit_one(
                product_id=product_id_vote_add,
                is_partial=True,
                orm_model=orm_model,
                rating_summary=orm_model.rating_summary + vote_add,
                voted_count=orm_model.voted_count + 1
            )
            if isinstance(orm_model, ORJSONResponse):
                return orm_model
            self.logger.info('Rating_summary was successfully increased')
            orm_models.append(orm_model)

        if product_id_vote_del:
            if vote_del is None :
                return ORJSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "message": Errors.HANDLER_MESSAGE,
                        "detail": "Value 'vote_add' must be valid integer",
                    }
                )
            orm_model = await self.get_or_create(
                product_id=product_id_vote_del,
            )
            if isinstance(orm_model, ORJSONResponse):
                return orm_model
            print('OOOOOOOORRRRRRRRRMMMMMM ', orm_model.voted_count, orm_model.rating_summary)
            orm_model = await self.edit_one(
                product_id=product_id_vote_del,
                is_partial=True,
                orm_model=orm_model,
                rating_summary=orm_model.rating_summary - vote_del,
                voted_count=orm_model.voted_count - 1
            )
            if isinstance(orm_model, ORJSONResponse):
                return orm_model
            self.logger.info('Rating_summary was successfully decreased')
            orm_models.append(orm_model)

        return orm_models

