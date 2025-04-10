import logging
from typing import Any, TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from fastapi_users import BaseUserManager, models, exceptions
from fastapi import Request, status
from fastapi_users.authentication import Strategy, AuthenticationBackend
from fastapi_users.exceptions import InvalidResetPasswordToken
from fastapi_users.router import ErrorCode
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from .exceptions import Errors

if TYPE_CHECKING:
    from src.core.models import User
    from src.api.v1.users.schemas import UserUpdate


class AuthService:
    def __init__(
        self,
        user_manager: BaseUserManager[models.UP, models.ID] | None = None,
        backend: AuthenticationBackend[models.UP, models.ID] | None = None,
    ):
        self.user_manager = user_manager
        self.backend = backend
        self.logger = logging.getLogger(__name__)

    async def login(
            self,
            request: Request,
            credentials: Any,
            strategy: Strategy[models.UP, models.ID],
            requires_verification: bool = False
    ):
        user = await self.user_manager.authenticate(credentials)
        if user is None or not user.is_active:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.BAD_CREDENTIALS_OR_NOT_ACTIVE,
                }
            )
        if requires_verification and not user.is_verified:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.user_not_verified_emailed(user.email),
                }
            )
        response = await self.backend.login(strategy, user)
        await self.user_manager.on_after_login(user, request, response)
        return response

    async def logout(
            self,
            token: tuple[models.UP, str],
            strategy: Strategy[models.UP, models.ID],
    ):
        user, token = token
        return await self.backend.logout(strategy, user, token)

    async def register(
            self,
            request: Request,
            user_create_schema: Any
    ):
        try:
            created_user = await self.user_manager.create(
                user_create_schema, safe=True, request=request
            )
        except exceptions.UserAlreadyExists:
            self.logger.warning("User %r already exists" % user_create_schema.email)
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.user_already_exists_emailed(user_create_schema.email),
                }
            )
        except exceptions.InvalidPasswordException as e:
            self.logger.warning("Invalid password while registration")
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.invalid_password_reasoned(e.reason),
                }
            )
        return created_user

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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.user_not_exists_mailed(email),
                }
            )
        except exceptions.UserInactive:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.inactive_user_emailed(email),
                }
            )
        except exceptions.UserAlreadyVerified:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.verify_user_already_verified_emailed(email),
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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.VERIFY_USER_BAD_TOKEN
                }
            )
        except exceptions.UserAlreadyVerified:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.VERIFY_USER_ALREADY_VERIFIED
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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.DATABASE_ERROR
                }
            )

    async def forgot_password(
            self,
            request: Request,
            email: Any,
    ):
        try:
            user = await self.user_manager.get_by_email(email)
        except exceptions.UserNotExists:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.user_not_exists_mailed(email)
                }
            )
        try:
            await self.user_manager.forgot_password(user, request)
        except exceptions.UserInactive:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.inactive_user_emailed(email)
                }
            )
        return None

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
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.INVALID_RESET_PASSWORD_TOKEN
                }
            )
