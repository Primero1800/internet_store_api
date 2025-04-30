import logging
from typing import TYPE_CHECKING, Optional

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import CartsRepository
from .schemas import (
    CartCreate,
    CartUpdate,
    CartPartialUpdate,
)
from .exceptions import Errors
from .validators import ValidRelationsInspector


if TYPE_CHECKING:
    from src.core.models import (
        Cart,
        User,
    )
    from .filters import CartFilter

CLASS = "Cart"
_CLASS = "cart"


class CartsService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all(
            self,
            filter_model: "CartFilter",
    ):
        repository: CartsRepository = CartsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "CartFilter"
    ):
        repository: CartsRepository = CartsRepository(
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
        repository: CartsRepository = CartsRepository(
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
            return await utils.get_short_schema_from_orm(orm_model=returned_orm_model)
        return returned_orm_model

    async def get_one_complex(
            self,
            id: int = None,
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        repository: CartsRepository = CartsRepository(
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
                    "message": Errors.HANDLER_MESSAGE,
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
            id: int,
            to_schema: bool = True
    ):
        repository: CartsRepository = CartsRepository(
            session=self.session
        )

        # catching ValidationError in exception_handler
        instance: CartCreate = CartCreate(
            user_id=id,
        )
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

        dict_to_validate = {}
        if isinstance(id, int):
            dict_to_validate['user_id'] = id
        inspector = ValidRelationsInspector(
            session=self.session,
            **dict_to_validate
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result
        # product_orm = result["product_orm"] if "product_orm" in result else None

        try:
            await repository.create_one_empty(orm_model=orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

        self.logger.info("%s %r was successfully created" % (CLASS, orm_model))
        return await self.get_one_complex(
            id=orm_model.user_id,
            to_schema=to_schema
        )

    async def delete_one(
            self,
            orm_model: "Cart",
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: CartsRepository = CartsRepository(
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
            orm_model: "Cart",
            id: int,
            is_partial: bool = False
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model
        repository: CartsRepository = CartsRepository(
            session=self.session,
        )

        # catching ValidationError in exception_handler
        updating_dictionary = {
            "user_id": id
        }
        if is_partial:
            instance: CartPartialUpdate = CartPartialUpdate(**updating_dictionary)
        else:
            instance: CartUpdate = CartUpdate(**updating_dictionary)

        dict_to_validate = {}
        if isinstance(id, int):
            dict_to_validate['user_id'] = id
        inspector = ValidRelationsInspector(
            session=self.session,
            **dict_to_validate
        )
        result = await inspector.inspect()
        if isinstance(result, ORJSONResponse):
            return result
        # product_orm = result["product_orm"] if "product_orm" in result else None

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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )

        self.logger.info("%s %r was successfully edited" % (CLASS, orm_model))

        return await self.get_one_complex(
            id=orm_model.user_id
        )

    async def get_or_create(
            self,
            user_id: int,
            to_schema: bool = False,
            maximized: bool = False,
    ):
        self.logger.info('Getting %r bound with user_id=%s from database' % (CLASS, user_id))
        sa_orm_model = await self.get_one_complex(
            id=user_id,
            to_schema=False
        )
        if isinstance(sa_orm_model, ORJSONResponse):
            self.logger.info('No %r bound with user_id=%s in database' % (CLASS, user_id))
            self.logger.info('Creating %r bound with user_id=%s in database' % (CLASS, user_id))
            sa_orm_model = await self.create_one(
                id=user_id,
                to_schema=False,
            )

        if to_schema:
            if not maximized:
                return await utils.get_short_schema_from_orm(sa_orm_model)
            else:
                return await utils.get_schema_from_orm(sa_orm_model)
        return sa_orm_model
