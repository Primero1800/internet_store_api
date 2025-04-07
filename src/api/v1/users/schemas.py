from typing import Annotated

from fastapi_users import schemas
from pydantic import Field


class BaseUser():

    firstname: Annotated[str | None, Field(
            max_length=50, min_length=2,
            default="John",
            description="User's firstname, used in application",
            title='User firstname'
    )]

    lastname: Annotated[str | None, Field(
            max_length=50, min_length=2,
            default="Doe",
            description="User's lastname, used in application",
            title='User lastname'
    )]


class UserRead(BaseUser, schemas.BaseUser[int]):
    pass


class UserCreate(BaseUser, schemas.BaseUserCreate):
    pass


class UserUpdate(BaseUser, schemas.BaseUserUpdate):
    pass
