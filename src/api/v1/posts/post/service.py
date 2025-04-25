import logging
from typing import TYPE_CHECKING, Optional

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import PostsRepository
from .schemas import (
    PostCreate,
    PostUpdate,
    PostPartialUpdate,
)
from .exceptions import Errors
from .validators import ValidRelationsInspector


if TYPE_CHECKING:
    from src.core.models import (
        Post,
        User,
    )
    from .filters import PostFilter

CLASS = "Post"
_CLASS = "post"


class PostsService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all(
            self,
            filter_model: "PostFilter",
    ):
        repository: PostsRepository = PostsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "PostFilter"
    ):
        repository: PostsRepository = PostsRepository(
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
        repository: PostsRepository = PostsRepository(
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
            await utils.get_short_schema_from_orm(returned_orm_model)
        return returned_orm_model

    async def get_one_complex(
            self,
            id: int = None,
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        repository: PostsRepository = PostsRepository(
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
            user: "User",
            name: str,
            product_id: Optional[int] = None,
            review: Optional[str] = None,
    ):
        repository: PostsRepository = PostsRepository(
            session=self.session
        )

        # catching ValidationError in exception_handler
        instance: PostCreate = PostCreate(
            user_id=user.id,
            product_id=product_id,
            name=name,
            review=review,
        )
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

        dict_to_validate = {}
        if isinstance(product_id, int):
            dict_to_validate['product_id'] = product_id
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
            id=orm_model.id
        )

    async def delete_one(
            self,
            orm_model: "Post",
            user: "User",
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: PostsRepository = PostsRepository(
            session=self.session
        )

        try:
            if not user.is_superuser and user.id != orm_model.user_id:
                raise CustomException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    msg=Errors.NO_RIGHTS
                )
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
            orm_model: "Post",
            user: "User",
            name: str,
            review: str,
            product_id: Optional[int] = None,
            reset_product: Optional[bool] = False,
            is_partial: bool = False
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model
        repository: PostsRepository = PostsRepository(
            session=self.session,
        )

        # catching ValidationError in exception_handler
        updating_dictionary = {
            "user_id": user.id,
            "product_id": product_id,
            "name": name,
            "review": review,
        }
        if is_partial:
            instance: PostPartialUpdate = PostPartialUpdate(**updating_dictionary)
        else:
            instance: PostUpdate = PostUpdate(**updating_dictionary)

        # inspecting if user is authorized to edit item
        if not user.is_superuser and user.id != orm_model.user_id:
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.NO_RIGHTS,
                }
            )

        dict_to_validate = {}
        if isinstance(product_id, int):
            dict_to_validate['product_id'] = product_id
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
                reset_product=reset_product,
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
            id=orm_model.id
        )