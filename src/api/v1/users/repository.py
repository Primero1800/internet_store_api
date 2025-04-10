import logging

from fastapi import status
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_users import BaseUserManager, models
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.users.exceptions import NoSessionException
from src.core.models import User

logger = logging.getLogger(__name__)


class UsersRepository:
    def __init__(
        self,
        session: AsyncSession | None = None,
        user_manager: BaseUserManager[models.UP, models.ID] | None = None,
    ):
        self.user_manager = user_manager
        self.session = session

    async def get_all_users(
            self,
            filter_model: Filter,
    ):
        if not self.session:
            logger.error(
                "Impossible to get all users from database, because no active session. "
                "Raised NoSessionException"
            )
            raise NoSessionException(
                status_code=status.HTTP_400_BAD_REQUEST,
                msg="No active sessions found"
            )

        query_filter = filter_model.filter(select(User))
        stmt = filter_model.sort(query_filter)
        # stmt = query_filter.order_by(User.id)
        result: Result = await self.session.execute(stmt)
        return result.scalars().all()
