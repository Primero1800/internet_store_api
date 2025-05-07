import logging
from fastapi import status
from typing import Union, TYPE_CHECKING

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
            user_id: int = None,
            maximized: bool = True,
            relations: list = []
    ):
        if not PERSON in self.session_data.data:
            text_error = f"user_id={user_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        person = self.session_data.data[PERSON]
        result = SessionPerson(**person)
        return result

    async def get_one(
            self,
            user_id: int = None,
    ):
        return await self.get_one_complex()

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

    async def create_one_empty(
            self,
            orm_model: SessionPerson
    ):
        if PERSON in self.session_data.data:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                msg=Errors.ALREADY_EXISTS()
            )
        session_service: SessionsService = SessionsService()

        result = await session_service.update_session(
            session_data=self.session_data,
            data_to_update={
                PERSON: orm_model.to_dict()
            },
            session_id=self.session_data.session_id
        )
        if isinstance(result, ORJSONResponse):
            raise CustomException(
                status_code=result.status_code,
                msg=result.content.get("detail")
            )
        result = SessionPerson(**result.data[PERSON])
        return result
