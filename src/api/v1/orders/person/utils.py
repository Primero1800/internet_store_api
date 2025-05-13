from typing import TYPE_CHECKING, Union, Any

from fastapi.responses import ORJSONResponse

from .schemas import (
    PersonRead,
    PersonShort,
)

if TYPE_CHECKING:
    from src.core.models import (
        Person,
    )
    from src.api.v1.orders.person.session_person import SessionPerson


async def get_schema_from_orm(
        orm_model: Union["Person", "SessionPerson", ORJSONResponse],
        maximized: bool = True,
        relations: list | None = None,
) -> Any:
    # BRUTE FORCE VARIANT

    if isinstance(orm_model, ORJSONResponse):
        return orm_model

    # short_schema: CartShort = await get_short_schema_from_orm(orm_model=orm_model)

    dict_to_push_to_schema = orm_model.to_dict()
    if 'user' in dict_to_push_to_schema:
        del dict_to_push_to_schema['user']

    user_short = None
    if maximized or (relations and 'user' in relations):
        if orm_model.user:
            from src.api.v1.users.user.utils import get_short_schema_from_orm as get_short_user_schema_from_orm
            user_short = await get_short_user_schema_from_orm(orm_model.user)
        if 'user' in relations:
            return user_short

    return PersonRead(
        **dict_to_push_to_schema,
        user=user_short
    )


async def get_short_schema_from_orm(
        orm_model: Union["Person", "SessionPerson", ORJSONResponse]
) -> PersonShort | ORJSONResponse:

    if isinstance(orm_model, ORJSONResponse):
        return orm_model

    # BRUTE FORCE VARIANT
    return PersonShort(
        **orm_model.to_dict(),
    )
