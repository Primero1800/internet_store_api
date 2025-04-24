import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union, TYPE_CHECKING

from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, models, exceptions, InvalidPasswordException
from sqlalchemy import Integer

from src.api.v1.email_sender.schemas import CustomMessageSchema
from src.core.settings import settings

if TYPE_CHECKING:
    from src.core.models import User
    from fastapi import Request, BackgroundTasks, Response


logger = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager["User", Integer]):

    reset_password_token_secret = settings.auth.AUTH_RESET_PASSWORD_TOKEN_SECRET
    reset_password_token_lifetime_seconds = settings.auth.AUTH_RESET_PASSWORD_TOKEN_LIFETIME_SECONDS
    verification_token_secret = settings.auth.AUTH_VERIFICATION_TOKEN_SECRET
    verification_token_lifetime_seconds = settings.auth.AUTH_VERIFICATION_TOKEN_LIFETIME_SECONDS

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional["Request"] = None,
        background_tasks: Optional["BackgroundTasks"] = None,
    ) -> models.UP:
        """
        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param background_tasks: Optional for usings BackgroundTasks inside manager
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request, background_tasks)

        return created_user

    async def on_after_register(
            self,
            user: "User",
            request: Optional["Request"] = None,
            background_tasks: Optional["BackgroundTasks"] = None,
    ):
        logger.warning("%r has registered." % (user, ))

        if not user.is_verified:
            from src.api.v1.auth.service import AuthService
            service = AuthService(
                user_manager=self
            )
            await service.request_verify_token(
                request=request,
                email=user.email,
            )

    async def on_after_request_verify(
        self,
        user: "User",
        token: str,
        request: Optional["Request"] = None
    ):
        logger.warning("Verification requested for %r. Verification token: %r" % (user, token))

        schema = CustomMessageSchema(
            recipients=[user.email, ],
            subject=settings.app.APP_TITLE + '. Registration',
            body=f"You have been registered on {settings.app.APP_TITLE}. "
                 f"To finish registration, please, use this token in "
                 f"{settings.auth.AUTH_VERIFICATION_TOKEN_LIFETIME_SECONDS // 60} min: {token}   "
                 f"or just follow the link: {settings.run.app_src.APP_HOST_SERVER_URL}"
                 f"{settings.auth.get_url(purpose='verify-hook', version='v1')}/?path={token}"
        )

        from src.api.v1.celery_tasks.tasks import task_send_mail
        task_send_mail.apply_async(args=(schema.model_dump(),))

    async def on_after_login(
            self, user: "User",
            request: Optional["Request"] = None,
            response: Optional["Response"] = None,
    ):
        logger.info("%r logged in." % (user,))
        from src.api.v1.auth.service import AuthService
        from src.api.v1.users.user.schemas import UserUpdateExtended
        service = AuthService(
            user_manager=self
        )
        await service.update_last_login(
            user=user,
            schema_update=UserUpdateExtended(last_login=datetime.now()),
            request=request,
        )

    async def on_after_forgot_password(
        self, user: "User", token: str, request: Optional["Request"] = None
    ):
        logger.warning("%r has forgot their password. Reset token will be sent to email" % user)
        schema = CustomMessageSchema(
            recipients=[user.email, ],
            subject=settings.app.APP_TITLE + '. Password changing.',
            body=f"You have been requested on {settings.app.APP_TITLE} "
                 f"for password restoring, please, use this token in "
                 f"{settings.auth.AUTH_RESET_PASSWORD_TOKEN_LIFETIME_SECONDS // 60} min: {token}   "
                 # f"or just follow the link: {settings.run.app_src.APP_HOST_SERVER_URL}"
                 # f"{settings.auth.get_url(purpose='reset-password-hook', version='v1')}"
                 # f"/?path={token}"
        )
        from src.api.v1.celery_tasks.tasks import task_send_mail
        task_send_mail.apply_async(args=(schema.model_dump(),))

    async def on_after_reset_password(
            self, user: "User", request: Optional["Request"] = None):
        logger.warning("%r has reset his password." % (user, ))

    async def on_after_update(
            self, user: "User", update_dict: Dict[str, Any],
            request: Optional["Request"] = None,
    ):
        logger.warning("%r has been updated with %r" % (user, update_dict))

    async def on_after_delete(
            self, user: "User", request: Optional["Request"] = None):
        logger.info("%r is successfully deleted" % (user, ))

    async def validate_password(
        self, password: str, user: Union[schemas.UC, models.UP]
    ) -> None:
        if len(password) < settings.users.USERS_PASSWORD_MIN_LENGTH:
            raise InvalidPasswordException(
                reason=f"Password should be at least "
                       f"{settings.users.USERS_PASSWORD_MIN_LENGTH} characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )
