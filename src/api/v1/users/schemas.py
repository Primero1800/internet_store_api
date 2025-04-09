from datetime import datetime
from typing import Annotated, Optional

from fastapi_users import schemas
from pydantic import Field

base_firstname = Annotated[str | None, Field(
            max_length=50, min_length=2,
            default="John",
            description="User's firstname, used in application",
            title='User firstname'
    )]

base_lastname = Annotated[str | None, Field(
            max_length=50, min_length=2,
            default="Doe",
            description="User's lastname, used in application",
            title='User lastname'
    )]

base_data_joined = Annotated[datetime, Field(
        description="The time and date, when user joined service",
        title='Data joined'
    )]

base_last_login = Annotated[datetime, Field(
        description="The time and date, when user logged in service last time",
        title='Last login'
    )]


class BaseUser():

    firstname: base_firstname
    lastname: base_lastname


class UserRead(BaseUser, schemas.BaseUser[int]):
    data_joined: base_data_joined
    last_login: Optional[base_last_login]


class UserCreate(BaseUser, schemas.BaseUserCreate):
    pass


class UserUpdate(BaseUser, schemas.BaseUserUpdate):
    last_login: Optional[base_last_login] = None
    firstname: Optional[base_firstname] = None
    lastname: Optional[base_lastname] = None
