import logging
from typing import TYPE_CHECKING, Optional

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import VotesRepository
from .schemas import (
    VoteCreate,
    VoteUpdate,
    VotePartialUpdate,
)
from .exceptions import Errors
from .validators import ValidRelationsInspector

from ..sale_information import utils as sale_info_utils

if TYPE_CHECKING:
    from src.core.models import (
        Vote,
        User,
    )
    from .filters import VoteFilter

CLASS = "Vote"
_CLASS = "vote"


class VotesService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all(
            self,
            filter_model: "VoteFilter",
    ):
        repository: VotesRepository = VotesRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "VoteFilter"
    ):
        repository: VotesRepository = VotesRepository(
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
        repository: VotesRepository = VotesRepository(
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
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
        if to_schema:
            return await utils.get_short_schema_from_orm(returned_orm_model)
        return returned_orm_model

    async def get_one_complex(
            self,
            id: int = None,
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        repository: VotesRepository = VotesRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one_complex(
                id=id,
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
            if not maximized and not relations:
                return await utils.get_short_schema_from_orm(
                    returned_orm_model
                )
            return await utils.get_schema_from_orm(
                returned_orm_model,
                maximized=maximized,
                relations=relations,
            )
        return returned_orm_model

    async def create_one(
            self,
            user: "User",
            product_id: int,
            name: str,
            stars: int,
            review: Optional[str] = None,
    ):
        repository: VotesRepository = VotesRepository(
            session=self.session
        )

        # catching ValidationError in exception_handler
        instance: VoteCreate = VoteCreate(
            user_id=user.id,
            product_id=product_id,
            name=name,
            review=review,
            stars=stars,
        )
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

        inspector = ValidRelationsInspector(
            session=self.session,
            **{"product_id": product_id}
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result
        # product_orm = result["product_orm"] if "product_orm" in result else None

        # storing data to recount rating in SaleInformation table
        data_to_restore_rating = {
            "product_id_vote_add": instance.product_id or orm_model.product_id,
            "vote_add": instance.stars or orm_model.stars,
        }

        try:
            await repository.create_one_empty(orm_model=orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        self.logger.info("%s %r was successfully created" % (CLASS, orm_model))

        # Editing rating according 'data_restore_rating'
        await sale_info_utils.do_vote(
            session=self.session,
            **data_to_restore_rating,
        )
        self.logger.info("Rating was successfully edited")

        return await self.get_one_complex(
            id=orm_model.id
        )

    async def delete_one(
            self,
            orm_model: "Vote",
            user: "User",
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: VotesRepository = VotesRepository(
            session=self.session
        )

        # storing data to recount rating in SaleInformation table
        data_to_restore_rating = {
            "product_id_vote_del": orm_model.product_id,
            "vote_del": orm_model.stars
        }

        try:
            if not user.is_superuser and user.id != orm_model.user_id:
                raise CustomException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    msg=Errors.NO_RIGHTS()
                )
            result = await repository.delete_one(orm_model=orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        # Editing rating according 'data_restore_rating'
        await sale_info_utils.do_vote(
            session=self.session,
            **data_to_restore_rating,
        )
        self.logger.info("Rating was successfully edited")
        return result

    async def edit_one(
            self,
            orm_model: "Vote",
            user: "User",
            product_id: int,
            name: str,
            review: str,
            stars: int,
            is_partial: bool = False
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model
        repository: VotesRepository = VotesRepository(
            session=self.session,
        )

        # catching ValidationError in exception_handler
        updating_dictionary = {
            "user_id": user.id,
            "product_id": product_id,
            "name": name,
            "review": review,
            "stars": stars,
        }
        if is_partial:
            instance: VotePartialUpdate = VotePartialUpdate(**updating_dictionary)
        else:
            instance: VoteUpdate = VoteUpdate(**updating_dictionary)

        # inspecting if user is authorized to edit item
        if not user.is_superuser and user.id != orm_model.user_id:
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": Errors.NO_RIGHTS(),
                }
            )

        inspector = ValidRelationsInspector(
            session=self.session,
            **{"product_id": product_id}
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result
        # product_orm = result["product_orm"] if "product_orm" in result else None

        # storing data to recount rating in SaleInformation table
        data_to_restore_rating = {
            "product_id_vote_add": instance.product_id or orm_model.product_id,
            "vote_add": instance.stars or orm_model.stars,
            "product_id_vote_del": orm_model.product_id,
            "vote_del": orm_model.stars
        }

        try:
            await repository.edit_one_empty(
                instance=instance,
                orm_model=orm_model,
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

        self.logger.info("%s %r was successfully edited" % (CLASS, orm_model))

        # Editing rating according 'data_restore_rating'
        await sale_info_utils.do_vote(
            session=self.session,
            **data_to_restore_rating,
        )
        self.logger.info("Rating was successfully edited")

        return await self.get_one_complex(
            id=orm_model.id
        )
