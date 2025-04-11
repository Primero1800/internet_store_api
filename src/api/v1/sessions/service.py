import uuid
from datetime import datetime
from typing import Any
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

    async def create_session(
            self,
            user: Any,
            response: Response,
    ):
        session_id = uuid.uuid5(uuid.NAMESPACE_DNS, user.email) if user and hasattr(user, "email") else uuid4()
        data = SessionData(
            user_id=user.id if user else None,
            user_email=user.email if user else None,
            data={
                "day": "monday",
                "time": datetime.now(tz=pytz.timezone("Europe/Moscow"))
            })
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
        result = await backend.read(session_id)
        if not result:
            self.logger.error("%r: %r" % (Errors.READ_EXISTING_SESSION_ERROR, user.email))
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": Errors.read_existing_session_error_id(session_id),
                }
            )
        return result
