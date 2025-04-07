import logging

from fastapi.responses import ORJSONResponse
from fastapi_users import BaseUserManager, models, exceptions
from fastapi import Request, status
from pydantic import EmailStr


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
