import logging
from typing import TYPE_CHECKING, Optional, Iterable, Any, Union

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.sessions.fastapi_sessions_config import SessionData
from src.tools.exceptions import CustomException
from . import utils
from .repository import PersonsRepository
from .schemas import (
    PersonCreate,
    PersonUpdate,
    PersonPartialUpdate,
)
from .exceptions import Errors
from .session_person.repository import SessionPersonsRepository


if TYPE_CHECKING:
    from src.core.models import (
        Person,
        User,
    )
    from src.api.v1.orders.person.session_person import (
        SessionPerson,
    )
    from .filters import PersonFilter


CLASS = "Person"
_CLASS = "person"


class PersonsService:
    def __init__(
            self,
            session: AsyncSession,
            session_data: Optional[SessionData] = None
    ):
        self.session = session
        self.session_data = session_data
        self.logger = logging.getLogger(__name__)

    async def get_all(
            self,
            filter_model: "PersonFilter",
            db_persons: Optional[bool] = None
    ):
        result = []
        if db_persons is True or db_persons is None:
            repository: PersonsRepository = PersonsRepository(
                session=self.session
            )
            listed_orm_models = await repository.get_all(filter_model=filter_model)
            for orm_model in listed_orm_models:
                result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        if db_persons is False or db_persons is None:
            repository: SessionPersonsRepository = SessionPersonsRepository(
                session_data=self.session_data
            )
            listed_orm_models = await repository.get_all()
            for orm_model in listed_orm_models:
                result.append(await utils.get_short_schema_from_orm(orm_model=orm_model))
        return result

    async def get_all_full(
            self,
            filter_model: "PersonFilter",
            db_persons: Optional[bool] = None
    ):
        result = []
        if db_persons is True or db_persons is None:
            repository: PersonsRepository = PersonsRepository(
                session=self.session
            )
            listed_orm_models = await repository.get_all_full(filter_model=filter_model)
            for orm_model in listed_orm_models:
                result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        if db_persons is False or db_persons is None:
            repository: SessionPersonsRepository = SessionPersonsRepository(
                session_data=self.session_data
            )
            listed_orm_models = await repository.get_all()
            for orm_model in listed_orm_models:
                result.append(await utils.get_schema_from_orm(orm_model=orm_model))
        return result

    async def get_one(
            self,
            cart_type: Any = None,
            user_id: Optional[int] = None,
            to_schema: bool = True
    ):
        if isinstance(cart_type, ORJSONResponse):
            return cart_type
        if cart_type and isinstance(cart_type, SessionData):
            repository: SessionPersonsRepository = SessionPersonsRepository(
                session_data=cart_type
            )
        else:
            repository: PersonsRepository = PersonsRepository(
                session=self.session
            )
        try:
            print('2222 rep 107', cart_type.id if hasattr(cart_type, "id") else user_id, cart_type) #########################################
            returned_orm_model = await repository.get_one(
                user_id=cart_type.id if hasattr(cart_type, "id") else user_id
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
        if to_schema:
            return await utils.get_short_schema_from_orm(orm_model=returned_orm_model)
        return returned_orm_model

    async def get_one_complex(
            self,
            user_id: int = None,
            cart_type: Any = None,
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        if isinstance(cart_type, ORJSONResponse):
            return cart_type
        if cart_type and isinstance(cart_type, SessionData):
            repository: SessionPersonsRepository = SessionPersonsRepository(
                session_data=cart_type
            )
        else:
            repository: PersonsRepository = PersonsRepository(
                session=self.session
            )
        try:
            returned_orm_model = await repository.get_one_complex(
                user_id=cart_type.id if hasattr(cart_type, "id") else user_id,
                maximized=maximized,
                relations=relations,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
        if to_schema:
            if not maximized and not relations:
                return await utils.get_short_schema_from_orm(
                    returned_orm_model
                )
            return await utils.get_schema_from_orm(
                returned_orm_model,
                maximized=maximized,
                relations=relations,
            )
        return returned_orm_model
