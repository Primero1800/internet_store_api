import logging
from typing import Union, TYPE_CHECKING, Optional

from fastapi.responses import ORJSONResponse

from src.api.v1.sessions.service import SessionsService
from src.core.sessions.fastapi_sessions_config import (
    SessionData,
)
from src.core.settings import settings
from src.tools.exceptions import CustomException
from . import SessionPerson
from ..exceptions import Errors

if TYPE_CHECKING:
    from ..schemas import (
        PersonCreate,
        PersonUpdate,
        PersonPartialUpdate,
    )

CLASS = "SessionPerson"
PERSON = settings.sessions.SESSION_PERSON


class SessionPersonsRepository:
    def __init__(
            self,
            session_data: SessionData
    ):
        self.session_data = session_data
        self.logger = logging.getLogger(__name__)

    async def get_one_complex(
            self,
            cart_type: SessionData,
            user_id: int = None,
            maximized: bool = True,
            relations: list = []
    ):
        if not PERSON in cart_type.data:
            text_error = f"user_id={user_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        person = cart_type.data[PERSON]
        result = SessionPerson(**person)
        return result

    async def get_all(
            self,
    ) -> list:
        session_service: SessionsService = SessionsService()
        all_sessions = await session_service.get_all()
        result = []
        for session_data in all_sessions:
            if hasattr(session_data, 'data') and PERSON in session_data.data:
                person = SessionPerson(**session_data.data[PERSON])
                result.append(person)
        return result

    async def get_orm_model_from_schema(
            self,
            instance: Union["PersonCreate", "PersonUpdate", "PersonPartialUpdate"],
    ):
        orm_model: SessionPerson = SessionPerson(**instance.model_dump())
        return orm_model
