from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.usertools_content import ToolsContent
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

    dictionary: dict = {**orm_model.to_dict()}
    dictionary['wishlist'] = ToolsContent.from_dict(dictionary['wishlist'])
    dictionary['comparison'] = ToolsContent.from_dict(dictionary['comparison'])
    dictionary['recently_viewed'] = ToolsContent.from_dict(dictionary['recently_viewed'])

    # BRUTE FORCE VARIANT
    return UserToolsShort(
        **dictionary,
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


# /get-or-create/me
# /get-or-create/{user_id}
async def get_or_create(
        user_id: int,
        session: AsyncSession,
) -> "UserTools":
    from .service import UserToolsService
    service = UserToolsService(
        session=session
    )
    return await service.get_or_create(user_id)
