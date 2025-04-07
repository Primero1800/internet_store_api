import logging
from typing import Optional, Dict, Any, Union, TYPE_CHECKING

from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, models, exceptions, InvalidPasswordException
from sqlalchemy import Integer

from src.core.auth.users_db import get_user_db
from src.core.settings import settings

if TYPE_CHECKING:
    from src.core.models import User
    from fastapi import Request, BackgroundTasks, Response


logger = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager["User", Integer]):

    reset_password_token_secret = settings.auth.AUTH_RESET_PASSWORD_TOKEN_SECRET
    verification_token_secret = settings.auth.AUTH_VERIFICATION_TOKEN_SECRET

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

    async def on_after_forgot_password(
        self, user: "User", token: str, request: Optional["Request"] = None
    ):
        logger.warning("%r has forgot their password. Reset token: %r" % (user, token))

    async def on_after_reset_password(
            self, user: "User", request: Optional["Request"] = None):
        logger.warning("%r has reset his password." % (user, ))

    async def on_after_request_verify(
        self, user: "User", token: str, request: Optional["Request"] = None
    ):
        logger.warning("Verification requested for %r. Verification token: %r" % (user, token))

    async def on_after_update(
            self, user: "User", update_dict: Dict[str, Any],
            request: Optional["Request"] = None,
    ):
        logger.warning("%r has been updated with %r" % (user, update_dict))

    async def on_after_delete(
            self, user: "User", request: Optional["Request"] = None):
        logger.info("%r is successfully deleted" % (user, ))

    async def on_after_login(
            self, user: "User",
            request: Optional["Request"] = None,
            response: Optional["Response"] = None,
    ):
        logger.info("%r logged in." % (user,))

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
