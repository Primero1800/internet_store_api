from typing import TYPE_CHECKING

from .schemas import UserPublic

if TYPE_CHECKING:
    from src.core.models import (
        User,
    )


async def get_short_schema_from_orm(
    orm_model: "User"
) -> UserPublic:

    # BRUTE FORCE VARIANT
    return UserPublic(
        **orm_model.to_dict()
    )