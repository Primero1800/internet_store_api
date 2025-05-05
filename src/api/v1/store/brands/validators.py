from typing import Type, TYPE_CHECKING

from fastapi.responses import ORJSONResponse

from src.tools.exceptions import CustomException
from src.tools.inspector import (
    ValidRelationsInspectorBase,
    ValidRelationsException,
)

from .exceptions import Errors

if TYPE_CHECKING:
    from src.tools.errors_base import ErrorsBase
    from src.core.models import Brand


async def inspecting_brand_exists(
        brand_id: int,
        inspector: "ValidRelationsInspectorBase" ,
        errors: Type["ErrorsBase"] = Errors,
):
    # Expecting if chosen brand exists
    try:
        from .repository import BrandsRepository
        repository: BrandsRepository = BrandsRepository(
            session=inspector.session,
        )
        orm_model: "Brand" = await repository.get_one_complex(id=brand_id, maximized=False)
        inspector.result['brand_orm'] = orm_model
    except CustomException as exc:
        inspector.error = ORJSONResponse(
            status_code=exc.status_code,
            content={
                "message": errors.HANDLER_MESSAGE(),
                "detail": exc.msg,
            }
        )
        raise ValidRelationsException
