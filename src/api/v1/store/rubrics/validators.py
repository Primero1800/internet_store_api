from typing import Type, TYPE_CHECKING

from fastapi.responses import ORJSONResponse

from src.tools.exceptions import CustomException
from src.tools.inspector import (
    ValidRelationsInspectorBase,
    ValidRelationsException,
)

from .exceptions import Errors
from ..products import utils as product_utils

if TYPE_CHECKING:
    from src.tools.errors_base import ErrorsBase
    from src.core.models import Rubric


async def inspecting_rubric_ids(
        inspector: ValidRelationsInspectorBase,
        rubric_ids: str | list
):
    # Expecting if rubric_ids format valid
    try:
        inspector.result['rubric_ids'] = await product_utils.temporary_fragment(ids=rubric_ids)
    except CustomException as exc:
        inspector.error = ORJSONResponse(
            status_code=exc.status_code,
            content={
                "message": Errors.HANDLER_MESSAGE(),
                "detail": exc.msg,
            }
        )
        raise ValidRelationsException()


async def inspecting_rubric_exists(
        rubric_ids: list,
        inspector: ValidRelationsInspectorBase,
        errors: Type["ErrorsBase"] = Errors,
):
    # Expecting if chosen rubric_ids are existing
    try:
        from .repository import RubricsRepository
        repository: RubricsRepository = RubricsRepository(
            session=inspector.session
        )
        orm_models = []
        for rubric_id in rubric_ids:
            orm_model: "Rubric" = await repository.get_one(id=rubric_id)
            orm_models.append(orm_model)
        inspector.result['rubric_orms'] = orm_models
    except CustomException as exc:
        inspector.error = ORJSONResponse(
            status_code=exc.status_code,
            content={
                "message": errors.HANDLER_MESSAGE(),
                "detail": exc.msg,
            }
        )
        raise ValidRelationsException
