from typing import TYPE_CHECKING

from src.api.v1.store.votes.schemas import VoteRead

if TYPE_CHECKING:
    from src.core.models import (
        Vote,
    )


async def get_short_schema_from_orm(
    orm_model: "Vote"
) -> VoteRead:

    # BRUTE FORCE VARIANT
    return VoteRead(
        **orm_model.to_dict(),
    )
