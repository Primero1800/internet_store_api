import uuid
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from fastapi import status, Response
from fastapi.responses import ORJSONResponse
from fastapi_sessions.backends.session_backend import BackendError

import logging
import pytz
from fastapi_sessions.frontends.session_frontend import FrontendError

from src.core.sessions.fastapi_sessions_config import (
    SessionData,
    BACKEND as backend,
    cookie,
)
from .exceptions import Errors


class SessionsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def get_session_id(user: Any):
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(user.id)) if user and hasattr(user, "id") else uuid4()

    # async def is_invalid_current_session(
    #         self,
    #         session_data: Any,
    # ):
    #     if not session_data:
    #         return ORJSONResponse(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             content={
    #                 "message": Errors.HANDLER_MESSAGE,
    #                 "detail": Errors.INVALID_SESSION,
    #             }
    #         )
    #     return False

    # async def is_invalid_session_id(
    #         self,
    #         session_id: Any
    # ):
    #     if isinstance(session_id, FrontendError):
    #         if str(session_id) == Errors.COOKIE_NO_SESSION:
    #             status_code = status.HTTP_403_FORBIDDEN
    #             detail = Errors.COOKIE_NO_SESSION
    #         elif str(session_id) == Errors.COOKIE_SESSION_INVALID_SIGNATURE:
    #             status_code = status.HTTP_401_UNAUTHORIZED
    #             detail = Errors.COOKIE_SESSION_INVALID_SIGNATURE
    #         else:
    #             status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    #             detail = str(session_id)
    #         return ORJSONResponse(
    #             status_code=status_code,
    #             content={
    #                 "message": Errors.HANDLER_MESSAGE,
    #                 "detail": detail,
    #             }
    #         )
    #     return False

    async def get_current_session(
            self,
            session_data: Any,
    ):
        # invalid_session_data = await self.is_invalid_current_session(session_data)
        # if not invalid_session_data:
        #     return session_data
        return session_data


    async def create_session(
            self,
            user: Any,
            response: Response,
            session_data: dict | None = None,
    ):
        session_id = SessionsService.get_session_id(user)
        data = SessionData(
            user_id=user.id if user else None,
            user_email=user.email if user else None,
            session_id = session_id,
            data={
                "time": datetime.now(tz=pytz.timezone("Europe/Moscow"))
            })

        if session_data and isinstance(session_data, dict):
            data.data.update(session_data)

        try:
            await backend.create(session_id, data)
        except BackendError as exc:
            self.logger.error("%r: %r" % (Errors.SESSION_EXISTS, user.email), exc_info=exc)
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.session_exists_mailed(user.email),
                }
            )
        cookie.attach_to_response(response, session_id)
        return await self.returning_session_data_after_operation(session_id)

    async def set_current_session(
            self,
            user: Any,
            response: Response,
            session_id: Any | None = None
    ):
        if not session_id:
            session_id = SessionsService.get_session_id(user)
        result = await backend.read(session_id)
        if not result:
            self.logger.error("%r: %r" % (Errors.SETTING_NOT_EXISTING_SESSION, session_id))
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.setting_not_existing_session_emailed(user.email),
                }
            )
        cookie.attach_to_response(response, session_id)
        return result

    async def delete_session(
            self,
            response: Response,
            session_id: uuid.UUID,
    ):
        # invalid_cookie = await self.is_invalid_session_id(session_id)
        # if invalid_cookie:
        #     return invalid_cookie

        await backend.delete(session_id)
        cookie.delete_from_response(response)
        return

    async def update_session(
            self,
            session_data: Any,
            data_to_update: dict,
            session_id: uuid.UUID,
    ):

        # invalid_session_data = await self.is_invalid_current_session(session_data)
        # if invalid_session_data:
        #     return invalid_session_data

        session_data.data.update(data_to_update)
        try:
            await backend.update(session_id, session_data)
        except BackendError as exc:
            self.logger.warning("%r, %r" % (Errors.UPDATING_NOT_EXISTS_SESSION, session_id))
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.UPDATING_NOT_EXISTS_SESSION,
                }
            )
        return await self.returning_session_data_after_operation(session_id)

    async def clear_session(
            self,
            session_data: Any,
            session_id: Any,
    ):
        # invalid_session_data = await self.is_invalid_current_session(session_data)
        # if invalid_session_data:
        #     return invalid_session_data

        session_data.data.clear()
        try:
            await backend.update(session_id, session_data)
        except BackendError as exc:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.UPDATING_NOT_EXISTS_SESSION,
                }
            )
        return await self.returning_session_data_after_operation(session_id)

    async def returning_session_data_after_operation(
            self,
            session_id: uuid.UUID,
    ):
        result = await backend.read(session_id)
        if not result:
            self.logger.error("%r: %r" % (Errors.READ_EXISTING_SESSION_ERROR, session_id))
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.read_existing_session_error_id(session_id),
                }
            )
        return result
