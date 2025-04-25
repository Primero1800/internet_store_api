from typing import TYPE_CHECKING

from src.api.v1.users.user.schemas import UserPublicExtended, UserReadExtended

if TYPE_CHECKING:
    from src.core.models import (
        User,
    )


async def get_schema_from_orm(
        orm_model: "User",
        maximized: bool = True,
        relations: list | None = [],
):

    # BRUTE FORCE VARIANT

    vote_shorts = []
    if maximized or "votes" in relations:
        from ...store.votes.utils import get_short_schema_from_orm as get_short_vote_schema_from_orm
        for vote in orm_model.votes:
            vote_shorts.append(await get_short_vote_schema_from_orm(vote))
        if "votes" in relations:
            return sorted(vote_shorts, key=lambda x: x.id)

    post_shorts = []
    if maximized or "posts" in relations:
        from ...posts.post.utils import get_short_schema_from_orm as get_short_post_schema_from_orm
        for post in orm_model.posts:
            post_shorts.append(await get_short_post_schema_from_orm(post))
        if "posts" in relations:
            return sorted(post_shorts, key=lambda x: x.id)

    return UserReadExtended(
        **orm_model.to_dict(),

        votes=sorted(vote_shorts, key=lambda x: x.id),
        posts=sorted(post_shorts, key=lambda x: x.id)
    )


async def get_short_schema_from_orm(
    orm_model: "User"
) -> UserPublicExtended:

    # BRUTE FORCE VARIANT
    return UserPublicExtended(
        **orm_model.to_dict()
    )