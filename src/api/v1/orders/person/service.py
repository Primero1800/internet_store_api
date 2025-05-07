import logging
from typing import TYPE_CHECKING, Optional, Iterable, Any, Union

from fastapi import status
from fastapi.responses import ORJSONResponse
from fastapi_sessions.backends.session_backend import BackendError
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
            obj_type: Any = None,
            user_id: Optional[int] = None,
            to_schema: bool = True
    ):
        if isinstance(obj_type, ORJSONResponse):
            return obj_type
        if obj_type and isinstance(obj_type, SessionData):
            repository: SessionPersonsRepository = SessionPersonsRepository(
                session_data=obj_type
            )
        else:
            repository: PersonsRepository = PersonsRepository(
                session=self.session
            )
        try:
            returned_orm_model = await repository.get_one(
                user_id=obj_type.id if hasattr(obj_type, "id") else user_id
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
            obj_type: Any = None,
            maximized: bool = True,
            relations: list | None = [],
            to_schema: bool = True,
    ):
        if isinstance(obj_type, ORJSONResponse):
            return obj_type
        if not user_id and obj_type and isinstance(obj_type, SessionData):
            repository: SessionPersonsRepository = SessionPersonsRepository(
                session_data=obj_type
            )
        else:
            repository: PersonsRepository = PersonsRepository(
                session=self.session
            )
        try:
            returned_orm_model = await repository.get_one_complex(
                user_id=obj_type.id if hasattr(obj_type, "id") else user_id,
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

    async def create_one(
            self,
            user: Union["User", Any],
            firstname: str,
            lastname: Optional[str] = None,
            company_name: Optional[str] = None,
            to_schema: bool = True,
    ):
        if not user and isinstance(self.session_data, BackendError):
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": "No authentication or session provided",
                }
            )

        if user:
            repository: PersonsRepository = PersonsRepository(
                session=self.session
            )
        else:
            repository: SessionPersonsRepository = SessionPersonsRepository(
                session_data=self.session_data
            )

        # catching ValidationError in exception_handler
        instance: PersonCreate = PersonCreate(
            user_id=user.id if user else None,
            firstname=firstname,
            lastname=lastname,
            company_name=company_name,
        )
        orm_model = await repository.get_orm_model_from_schema(instance=instance)

        try:
            await repository.create_one_empty(
                orm_model=orm_model
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        self.logger.info("%s %r was successfully created" % (CLASS, orm_model))
        return await self.get_one_complex(
            user_id=orm_model.user_id,
            obj_type=self.session_data,
            to_schema=to_schema,
        )

    async def delete_one(
            self,
            orm_model: "Person",
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        repository: PersonsRepository = PersonsRepository(
            session=self.session
        )
        try:
            return await repository.delete_one(orm_model=orm_model)
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

    async def edit_one(
            self,
            orm_model: Union["Person", "SessionPerson"],
            firstname: Optional[str] = None,
            lastname: Optional[str] = None,
            company_name: Optional[str] = None,
            is_partial: bool = False,
            to_schema: bool = True,
    ):
        if orm_model and isinstance(orm_model, ORJSONResponse):
            return orm_model

        if isinstance(orm_model.user_id, int):
            repository: PersonsRepository = PersonsRepository(
                session=self.session,
            )
        else:
            repository: SessionPersonsRepository = SessionPersonsRepository(
                session_data=self.session_data
            )

        # catching ValidationError in exception_handler
        updating_dictionary = {
            "company_name": company_name,
            "firstname": firstname,
            "lastname": lastname,
        }
        if is_partial:
            instance: PersonPartialUpdate = PersonPartialUpdate(**updating_dictionary)
        else:
            instance: PersonUpdate = PersonUpdate(**updating_dictionary)

        try:
            await repository.edit_one_empty(
                instance=instance,
                orm_model=orm_model,
                is_partial=is_partial,
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )

        self.logger.info("%s %r was successfully edited" % (CLASS, orm_model))
        return await self.get_one_complex(
            user_id=orm_model.user_id,
            obj_type=self.session_data,
            to_schema=to_schema,
        )
