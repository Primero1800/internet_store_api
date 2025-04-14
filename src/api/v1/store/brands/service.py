import logging

from fastapi import UploadFile, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from . import utils
from .repository import BrandsRepository
from .schemas import BrandCreate
from .exceptions import Errors
from ..utils.image_utils import save_image


CLASS = "Brand"
_CLASS = "brand"


class BrandsService:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all(self):
        repository: BrandsRepository = BrandsRepository(
            session=self.session
        )
        result = []
        listed_orm_models = await repository.get_all()
        for orm_model in listed_orm_models:
            result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def create_one(
            self,
            title: str,
            description: str,
            image_schema: UploadFile,
    ):
        repository: BrandsRepository = BrandsRepository(
            session=self.session
        )

        # catching ValidationError in exception_handler
        instance: BrandCreate = BrandCreate(title=title, description=description)
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.IMAGE_SAVING_ERROR,
                }
            )

        self.logger.info("Image %r was successfully written" % image_schema)

        try:
            await repository.create_brand_image(
                file=file_path,
                orm_model=orm_model
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
        try:
            returned_orm_model = await repository.get_one_complex(
                id=orm_model.id,
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
