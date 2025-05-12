import json
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
from src.tools.phone_number import AppPhoneNumber
from . import SessionAddress
from ..exceptions import Errors

if TYPE_CHECKING:
    from ..schemas import (
        AddressCreate,
        AddressUpdate,
        AddressPartialUpdate,
    )

CLASS = "SessionAddress"
ADDRESS = settings.sessions.SESSION_ADDRESS


class SessionAddressesRepository:
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
        if not ADDRESS in self.session_data.data:
            text_error = f"user_id={user_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        address = self.session_data.data[ADDRESS]
        result = SessionAddress(**address)
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
            if hasattr(session_data, 'data') and ADDRESS in session_data.data:
                address = SessionAddress(**session_data.data[ADDRESS])
                result.append(address)
        return result

    async def get_orm_model_from_schema(
            self,
            instance: Union["AddressCreate", "AddressUpdate", "AddressPartialUpdate"],
    ):
        if hasattr(instance, "phonenumber") and isinstance(instance.phonenumber, AppPhoneNumber):
            instance.phonenumber = AppPhoneNumber.json_encode(instance.phonenumber)

        orm_model: SessionAddress = SessionAddress(**instance.model_dump())
        return orm_model

    async def create_one_empty(
            self,
            orm_model: SessionAddress
    ):
        if ADDRESS in self.session_data.data:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                msg=Errors.ALREADY_EXISTS()
            )

        self.logger.warning(f"Creating %r in session" % orm_model)
        session_service: SessionsService = SessionsService()

        result = await session_service.update_session(
            session_data=self.session_data,
            data_to_update={
                ADDRESS: orm_model.to_dict()
            },
            session_id=self.session_data.session_id
        )
        if isinstance(result, ORJSONResponse):
            self.logger.error("Error occurred while creating data in session")
            raise CustomException(
                status_code=result.status_code,
                msg=json.loads(result.body.decode()).get('detail')
            )
        result = SessionAddress(**result.data[ADDRESS])
        return result

    async def edit_one_empty(
            self,
            instance:  Union["AddressUpdate", "AddressPartialUpdate"],
            orm_model: SessionAddress,
            is_partial: bool = False
    ):
        for key, val in instance.model_dump(
                exclude_unset=is_partial,
                exclude_none=is_partial,
        ).items():
            if key == "phonenumber":
                val = AppPhoneNumber.json_encode(val)
            setattr(orm_model, key, val)

        self.logger.warning(f"Editing %r in session" % orm_model)
        session_service: SessionsService = SessionsService()

        result = await session_service.update_session(
            session_data=self.session_data,
            data_to_update={
                ADDRESS: orm_model.to_dict()
            },
            session_id=self.session_data.session_id
        )
        if isinstance(result, ORJSONResponse):
            self.logger.error("Error occurred while editing data in session")
            raise CustomException(
                status_code=result.status_code,
                msg=json.loads(result.body.decode()).get('detail')
            )
        result = SessionAddress(**result.data[ADDRESS])
        return result
