import logging
from datetime import datetime
from typing import Union, TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.sessions.service import SessionsService
from src.core.sessions.fastapi_sessions_config import (
    SessionData,
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
        if not CART in cart_type.data:
            text_error = f"user_id={id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        cart = cart_type.data[CART]
        result = SessionCart(**cart)
        return result

    async def get_orm_model_from_schema(
            self,
            instance: Union["CartCreate", "CartUpdate", "CartPartialUpdate"],
    ):
        orm_model: SessionCart = SessionCart(**instance.model_dump())
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
        result =  SessionCart(**result.data[CART])
        return result
