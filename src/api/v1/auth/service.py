import logging
from typing import Any, TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from fastapi_users import BaseUserManager, models, exceptions, schemas
from fastapi import Request, status
from fastapi_users.exceptions import InvalidResetPasswordToken
from fastapi_users.router import ErrorCode
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

if TYPE_CHECKING:
    from src.core.models import User
    from src.api.v1.users.schemas import UserUpdate


class AuthService:
    def __init__(
        self,
        user_manager: BaseUserManager[models.UP, models.ID]
    ):
        self.user_manager = user_manager
        self.logger = logging.getLogger(__name__)

    async def request_verify_token(
            self,
            request: Request,
            email: EmailStr
    ):

        try:
            user = await self.user_manager.get_by_email(email)
            await self.user_manager.request_verify(user, request)
        except exceptions.UserNotExists:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Handled by Service exception handler",
                    "detail": f"Email {email!r} isn't bound to any user",
                }
            )
        except exceptions.UserInactive:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Handled by Service exception handler",
                    "detail": f"User {user.email!r} is inactive.",
                }
            )
        except exceptions.UserAlreadyVerified:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Handled by Service exception handler",
                    "detail": f"User {user.email!r} is already verified",
                }
            )
        return {
            "message": f"Token was successfully send to email {user.email!r}"
        }

    async def verify(
            self,
            request: Request,
            token: str,
            schema: Any
    ):

        try:
            user = await self.user_manager.verify(request=request, token=token)
            return schema(**user.to_dict())

        except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Handled by Service exception handler",
                    "detail": ErrorCode.VERIFY_USER_BAD_TOKEN
                }
            )
        except exceptions.UserAlreadyVerified:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Handled by Service exception handler",
                    "detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED
                }
            )

    async def update_last_login(
            self,
            schema_update: "UserUpdate",
            user: "User",
            request: Request,
    ):
        try:
            return await self.user_manager.update(
                user_update=schema_update,
                user=user,
                request=request
            )
        except IntegrityError as exc:
            self.logger.error("Error while updating last loging information for user %r" % user.email, exc_info=exc)
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "Handled by Service exception handler",
                    "detail": "Internal server error while changing db data."
                }
            )

    async def reset_password(
            self,
            token: str,
            password: str,
            request: Request,
    ):
        try:
            return await self.user_manager.reset_password(
                token=token,
                password=password,
                request=request,
            )
        except InvalidResetPasswordToken as exc:
            self.logger.error("Error while changing password", exc_info=exc)
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Handled by Service exception handler",
                    "detail": f"Error while changing password: {exc}"
                }
            )
