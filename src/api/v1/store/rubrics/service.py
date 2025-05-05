import logging
from typing import TYPE_CHECKING

from fastapi import UploadFile, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import RubricsRepository
from .schemas import (
    RubricCreate,
    RubricUpdate,
    RubricPartialUpdate,
)
from .exceptions import Errors
from ..utils.image_utils import save_image

if TYPE_CHECKING:
    from src.core.models import Rubric
    from .filters import RubricFilter


CLASS = "Rubric"
_CLASS = "rubric"


class RubricsService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all(
            self,
            filter_model: "RubricFilter",
    ):
        repository: RubricsRepository = RubricsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all(filter_model=filter_model)
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "RubricFilter",
    ):
        repository: RubricsRepository = RubricsRepository(
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
        repository: RubricsRepository = RubricsRepository(
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
            slug: str = None,
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        repository: RubricsRepository = RubricsRepository(
            session=self.session
        )
        try:
            returned_orm_model = await repository.get_one_complex(
                id=id,
                slug=slug,
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
        if not maximized and not relations:
            return await utils.get_short_schema_from_orm(
                returned_orm_model
            )
        return await utils.get_schema_from_orm(
            returned_orm_model,
            maximized=maximized,
            relations=relations,
        )

    async def create_one(
            self,
            title: str,
            description: str,
            image_schema: UploadFile,
    ):
        repository: RubricsRepository = RubricsRepository(
            session=self.session
        )

        # catching ValidationError in exception_handler
        instance: RubricCreate = RubricCreate(title=title, description=description)
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

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

        try:
            file_path: str = await save_image(
                image_object=image_schema,
                path=f"media/{_CLASS}s",
                folder=f"{orm_model.id}"
            )
        except Exception as exc:
            self.logger.error("Error wile writing file", exc_info=exc)
            await repository.delete_one(
                orm_model=orm_model
            )
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": Errors.IMAGE_SAVING_ERROR(),
                }
            )

        self.logger.info("Image %r was successfully written" % image_schema)

        try:
            await repository.create_rubric_image(
                file=file_path,
                orm_model=orm_model
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        self.logger.info("Brand %r was successfully created" % orm_model)

        return await self.get_one_complex(
            id=orm_model.id
        )

    async def delete_one(
            self,
            orm_model: "Rubric",
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: RubricsRepository = RubricsRepository(
            session=self.session
        )
        try:
            return await repository.delete_one(orm_model=orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

    async def edit_one(
            self,
            title: str,
            description: str,
            image_schema: UploadFile,
            orm_model: "Rubric",
            is_partial: bool = False
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model
        repository: RubricsRepository = RubricsRepository(
            session=self.session,
        )

        # catching ValidationError in exception_handler
        if is_partial:
            instance: RubricPartialUpdate = RubricPartialUpdate(title=title, description=description)
        else:
            instance: RubricUpdate = RubricUpdate(title=title, description=description)

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

        if image_schema:
            try:
                file_path: str = await save_image(
                    image_object=image_schema,
                    path=f"media/{_CLASS}s",
                    folder=f"{orm_model.id}"
                )
            except Exception as exc:
                self.logger.error("Error wile writing file", exc_info=exc)
                return ORJSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "message": Errors.HANDLER_MESSAGE(),
                        "detail": Errors.IMAGE_SAVING_ERROR(),
                    }
                )

            self.logger.info("Image %r was successfully written" % image_schema)

            try:
                await repository.edit_rubric_image(
                    file=file_path,
                    orm_model=orm_model
                )
            except CustomException as exc:
                return ORJSONResponse(
                    status_code=exc.status_code,
                    content={
                        "message": Errors.HANDLER_MESSAGE(),
                        "detail": exc.msg,
                    }
                )

        self.logger.info("Rubric %r was successfully edited" % orm_model)
        return await self.get_one_complex(
            id=orm_model.id
        )
