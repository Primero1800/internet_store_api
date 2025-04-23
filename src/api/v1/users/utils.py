from typing import TYPE_CHECKING

from .schemas import UserPublicExtended

if TYPE_CHECKING:
    from src.core.models import (
        User,
    )


async def get_short_schema_from_orm(
    orm_model: "User"
) -> UserPublicExtended:

    # BRUTE FORCE VARIANT
    return UserPublicExtended(
        **orm_model.to_dict()
    )