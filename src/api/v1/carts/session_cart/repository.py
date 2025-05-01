import logging
import uuid
from datetime import datetime
from typing import Union, TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.sessions.service import SessionsService
from src.core.sessions.fastapi_sessions_config import (
    SessionData,
    BACKEND as backend,
)
from src.core.settings import settings
from src.tools.exceptions import CustomException
from . import SessionCart

if TYPE_CHECKING:
    from ..schemas import (
        CartCreate,
        CartUpdate,
        CartPartialUpdate,
        CartItemCreate,
        CartItemUpdate,
        CartItemPartialUpdate,
    )

CLASS = "SessionCart"
CART = settings.sessions.SESSION_CART


class SessionCartsRepository:
    def __init__(
            self,
            session_data: SessionData,
            # session: AsyncSession,
    ):
        # self.session=session,
        self.session_data = session_data
        self.logger = logging.getLogger(__name__)

    async def get_one_complex(
            self,
            cart_type: SessionData,
            id: int = None,
            maximized: bool = True,
            relations: list = []
    ):
        print('333333333333333333333333', cart_type) #####################################################
        if not CART in cart_type.data:
            text_error = f"user_id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        cart = cart_type.data[CART]
        print('3333333333333333333333333 rep 55', cart) ###############################################################################
        result = SessionCart(**cart)
        print('3333333333333333333333333 rep 57', result.created, type(result.created))  ################################################################
        return result

    async def get_orm_model_from_schema(
            self,
            instance: Union["CartCreate", "CartUpdate", "CartPartialUpdate"],
    ):
        orm_model: SessionCart = SessionCart(**instance.model_dump())
        print('TIIIMEEEEEEEEEEE', orm_model.created, orm_model.to_dict())
        return orm_model

    async def create_one_empty(
            self,
            orm_model: SessionCart
    ):
        session_service: SessionsService = SessionsService()

        result = await session_service.update_session(
            session_data=self.session_data,
            data_to_update={
                CART: orm_model.to_dict()
            },
            session_id=self.session_data.session_id
        )
        if isinstance(result, ORJSONResponse):
            raise CustomException(
                status_code=result.status_code,
                msg=result.content.get("detail")
            )
        print('2222222222222222222222222222 rep 84', result, type(result)) #######################################################
        result =  SessionCart(**result.data[CART])
        print('222222222222222 rep 86', result, type(result), result.created, type(result.created)) ####################################################################
        return result


