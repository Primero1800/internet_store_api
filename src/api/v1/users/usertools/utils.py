from typing import TYPE_CHECKING, Any

from ..user.utils import get_short_schema_from_orm as get_short_user_schema_from_orm

from .schemas import (
    UserToolsShort,
    UserToolsRead,
)

if TYPE_CHECKING:
    from src.core.models import (
        UserTools,
    )


CLASS = "UserTools"


async def get_short_schema_from_orm(
    orm_model: "UserTools"
) -> UserToolsShort:

    # BRUTE FORCE VARIANT
    return UserToolsShort(
        **orm_model.to_dict(),
    )


async def get_schema_from_orm(
    orm_model: "UserTools",
    maximized: bool = True,
    relations: list | None = [],
) -> UserToolsRead | Any:

    # BRUTE FORCE VARIANT

    short_schema: UserToolsShort = await get_short_schema_from_orm(orm_model=orm_model) if maximized else {}

    user_short = None
    if maximized or 'user' in relations:
        user_short = await get_short_user_schema_from_orm(orm_model.user)
    if 'user' in relations:
        return user_short

    return UserToolsRead(
        **short_schema.model_dump(),
        user=user_short
    )