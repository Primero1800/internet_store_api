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
    from src.core.models import User


async def inspecting_user_exists(
        user_id: int,
        inspector: "ValidRelationsInspectorBase" ,
        errors: Type["ErrorsBase"] = Errors,
):
    # Expecting if chosen user exists
    try:
        from .repository import UsersRepository
        users_repository: UsersRepository = UsersRepository(
            session=inspector.session,
        )
        user_orm: "User" = await users_repository.get_one_complex(id=user_id, maximized=False)
        inspector.result['user_orm'] = user_orm
    except CustomException as exc:
        inspector.error = ORJSONResponse(
            status_code=exc.status_code,
            content={
                "message": errors.HANDLER_MESSAGE(),
                "detail": exc.msg,
            }
        )
        raise ValidRelationsException
