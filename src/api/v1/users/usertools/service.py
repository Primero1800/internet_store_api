import datetime
import logging
from typing import TYPE_CHECKING, Optional

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from src.tools.usertools_content import ToolsContent
from .repository import UserToolsRepository
from .exceptions import Errors
from .validators import ValidRelationsInspector
from .schemas import (
    UserToolsCreate,
    UserToolsUpdate,
)
from . import utils

if TYPE_CHECKING:
    from .filters import UserToolsFilter
    from src.core.models import (
        UserTools,
        Product,
    )

CLASS = "UserTools"
_CLASS = "user_tools"


class UserToolsService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.repository = None

    async def get_all(
            self,
            filter_model: "UserToolsFilter",
    ):
        repository: UserToolsRepository = UserToolsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "UserToolsFilter"
    ):
        repository: UserToolsRepository = UserToolsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all_full(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        return result

    async def get_one(
            self,
            user_id: int = None,
            to_schema: bool = True,
    ):
        repository: UserToolsRepository = UserToolsRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one(
                user_id=user_id,
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
            user_id: int = None,
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        repository: UserToolsRepository = UserToolsRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one_complex(
                user_id=user_id,
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
            user_id: int,
            to_schema: Optional[bool] = True,
    ):
        repository: UserToolsRepository = UserToolsRepository(
            session=self.session
        )
        self.repository = repository

        # Expecting if UserCreate data valid
                # catching ValidationError in exception_handler
        instance: UserToolsCreate = UserToolsCreate(
            user_id=user_id,
        )
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

        inspector = ValidRelationsInspector(
            session=self.session,
            **{"user_id": user_id}
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

        self.logger.info("%s for User id=%s was successfully created" % (CLASS, orm_model.user_id))

        return await self.get_one_complex(
            user_id=orm_model.user_id,
            to_schema=to_schema,
        )

    async def delete_one(
            self,
            orm_model: "UserTools",
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: UserToolsRepository = UserToolsRepository(
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
            user_id: int,
            orm_model: "UserTools",
            is_partial: bool = False,
            to_schema: Optional[bool] = True
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: UserToolsRepository = UserToolsRepository(
            session=self.session
        )
        self.repository = repository

        # Expecting if Update or PartialUpdate data valid
        # catching ValidationError in exception_handler
        updating_dictionary = {
            "user_id": user_id,
        }
        if is_partial:
            return
        else:
            instance: UserToolsUpdate = UserToolsUpdate(**updating_dictionary)

        inspector = ValidRelationsInspector(
            session=self.session,
            **{"user_id": user_id}
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

        self.logger.info("%s for User id=%s was successfully edited" % (CLASS, orm_model.user_id))

        return await self.get_one_complex(
            user_id=orm_model.user_id,
            to_schema=to_schema,
        )

    async def get_or_create(
            self,
            user_id: int,
            to_schema: bool = False
    ):
        self.logger.info('Getting %r bound with user_id=%s from database' % (CLASS, user_id))
        sa_orm_model = await self.get_one(
            user_id=user_id,
            to_schema=False
        )
        if isinstance(sa_orm_model, ORJSONResponse):
            self.logger.info('No %r bound with user_id=%s in database' % (CLASS, user_id))
            self.logger.info('Creating %r bound with user_id=%s in database' % (CLASS, user_id))
            sa_orm_model = await self.create_one(
                user_id=user_id,
                to_schema=False,
            )
        if to_schema:
            return await utils.get_short_schema_from_orm(sa_orm_model)
        return sa_orm_model

    async def add_to_list(
            self,
            usertools: "UserTools",
            product: "Product",
            add_to: str = 'rv',
            to_schema: bool = False
    ):
        if isinstance(product, ORJSONResponse):
            return product

        content: ToolsContent = ToolsContent(
            product_id=product.id,
            added=datetime.datetime.now()
        )

        repository: UserToolsRepository = UserToolsRepository(
            session=self.session
        )

        try:
            orm_model = await repository.add_to_dict(
                usertools=usertools,
                content=content,
                add_to=add_to
            )
        except CustomException as exc:
            self.logger.error(Errors.DATABASE_ERROR, exc_info=exc)
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        if to_schema:
            return await utils.get_short_schema_from_orm(orm_model)
        return orm_model

    async def del_from_list(
            self,
            usertools: "UserTools",
            product_id: int,
            del_from: str = 'rv',
            to_schema: bool = False
    ):
        repository: UserToolsRepository = UserToolsRepository(
            session=self.session
        )
        try:
            orm_model = await repository.del_from_dict(
                usertools=usertools,
                product_id=product_id,
                del_from=del_from
            )
        except CustomException as exc:
            self.logger.error(Errors.DATABASE_ERROR, exc_info=exc)
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        if to_schema:
            return await utils.get_short_schema_from_orm(orm_model)
        return orm_model

    async def clear_list(
            self,
            usertools: "UserTools",
            del_from: str = 'rv',
            to_schema: bool = False
    ):
        repository: UserToolsRepository = UserToolsRepository(
            session=self.session
        )
        try:
            orm_model = await repository.clear_dict(
                usertools=usertools,
                del_from=del_from
            )
        except CustomException as exc:
            self.logger.error(Errors.DATABASE_ERROR, exc_info=exc)
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        if to_schema:
            return await utils.get_short_schema_from_orm(orm_model)
        return orm_model

    async def get_list(
            self,
            usertools: "UserTools",
            source: str = 'rv',
            to_schema: bool = False
    ):
        if source == 'w':
            product_ids = [int(key) for key in usertools.wishlist.keys()]
        elif source == "c":
            product_ids = [int(key) for key in usertools.comparison.keys()]
        else: # source == "rv"
            product_ids = [int(key) for key in usertools.recently_viewed.keys()]
        if not product_ids:
            return []

        from ...store.products.service import ProductsService
        prod_service: ProductsService = ProductsService(
            session=self.session
        )
        products = []
        for product_id in product_ids:
            product = await prod_service.get_one_complex(id=product_id)
            if isinstance(product, ORJSONResponse):
                return product
            products.append(product)

        return products
