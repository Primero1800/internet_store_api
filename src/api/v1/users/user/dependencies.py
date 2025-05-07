from typing import Union, TYPE_CHECKING

from fastapi import Depends, status, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi_sessions.backends.session_backend import BackendError
from fastapi_users import models, BaseUserManager, exceptions

from src.api.v1.auth.backend import fastapi_users
from src.api.v1.auth.dependencies import get_user_manager
from src.core.sessions.fastapi_sessions_config import verifier_or_none
from .exceptions import Errors

if TYPE_CHECKING:
    from src.core.models import (
        User,
    )
    from src.core.sessions.fastapi_sessions_config import SessionData

current_user = fastapi_users.current_user(
    active=True,
    verified=True,
)

current_superuser = fastapi_users.current_user(
    active=True,
    verified=True,
    superuser=True,
)

current_user_or_none = fastapi_users.current_user(
    optional=True,
    active=True,
    verified=True,
)

current_user_token = fastapi_users.authenticator.current_user_token(
    optional=False,
    active=False,
    verified=False,
    superuser=False,
)


async def get_user_or_404(
        id: str,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
) -> models.UP:
    try:
        parsed_id = user_manager.parse_id(id)
        return await user_manager.get(parsed_id)
    except (exceptions.UserNotExists, exceptions.InvalidID) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


async def user_cookie_or_error(
        user: "User" = Depends(current_user_or_none),
        session_data: "SessionData" = Depends(verifier_or_none),
) -> Union["User", "SessionData", ORJSONResponse]:
    if user:
        return user
    if session_data and not isinstance(session_data, BackendError):
        return session_data
    return ORJSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "message": Errors.HANDLER_MESSAGE(),
            "detail": "No authentication or session provided",
        }
    )
