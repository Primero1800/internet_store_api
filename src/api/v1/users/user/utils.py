from typing import TYPE_CHECKING

from fastapi_users import BaseUserManager, models
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.users.user.schemas import UserPublicExtended, UserReadExtended

if TYPE_CHECKING:
    from src.core.models import (
        User,
    )


async def get_schema_from_orm(
        orm_model: "User",
        maximized: bool = True,
        relations: list | None = None,
):

    # BRUTE FORCE VARIANT

    vote_shorts = []
    if maximized or (relations and "votes" in relations):
        from ...store.votes.utils import get_short_schema_from_orm as get_short_vote_schema_from_orm
        for vote in orm_model.votes:
            vote_shorts.append(await get_short_vote_schema_from_orm(vote))
        if relations and "votes" in relations:
            return sorted(vote_shorts, key=lambda x: x.id)

    post_shorts = []
    if maximized or (relations and "posts" in relations):
        from ...posts.post.utils import get_short_schema_from_orm as get_short_post_schema_from_orm
        for post in orm_model.posts:
            post_shorts.append(await get_short_post_schema_from_orm(post))
        if relations and "posts" in relations:
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


async def create_default_superuser(
    session: AsyncSession,
    user_manager: BaseUserManager[models.UP, models.ID],
):
    from .service import UsersService
    service: UsersService = UsersService(
        session=session,
        user_manager=user_manager
    )
    return await service.create_default_superuser()
