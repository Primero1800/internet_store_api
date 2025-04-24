from datetime import datetime, date
from typing import Optional

from pydantic import Field
from fastapi_filter.contrib.sqlalchemy import Filter

from src.core.models import User


class UserFilter(Filter):
    order_by: Optional[list[str]] = ['id']

    email__like: Optional[str] = Field(default=None, description="Filter by email contains", )
    is_active: Optional[bool] = Field(default=None, description="Filter whether user is active")
    is_verified: Optional[bool] = Field(default=None, description="Filter whether user is verified")
    is_superuser: Optional[bool] = Field(default=None, description="Filter whether user is superuser")
    data_joined__gte: Optional[date] = Field(default=None, description="Filter by data_joined after", )
    data_joined__lte: Optional[date] = Field(default=None, description="Filter by data_joined before", )
    last_login__lte: Optional[datetime] = Field(default=None, description="Filter by last_login before", )
    last_login__isnull: Optional[bool] = Field(default=None, description="Filter by never logged in before", )

    class Constants(Filter.Constants):
        model = User

    class Config:
        populated_by_name = True
