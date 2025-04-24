from fastapi import Depends, status, HTTPException
from fastapi_users import models, BaseUserManager, exceptions

from src.api.v1.auth.backend import fastapi_users
from src.api.v1.auth.dependencies import get_user_manager

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
