import uuid
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from fastapi import status, Response
from fastapi.responses import ORJSONResponse
from fastapi_sessions.backends.session_backend import BackendError

import logging
import pytz

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
        await backend.delete(session_id)
        cookie.delete_from_response(response)
        return

    async def update_session(
            self,
            session_data: Any,
            data_to_update: dict,
            session_id: uuid.UUID,
    ):

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
