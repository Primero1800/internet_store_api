import contextlib

import asyncio

from src.api.v1.auth.dependencies import get_user_manager
from src.core.auth.users_db import get_user_db
from src.core.config import DBConfigurer


async def main():
    from src.api.v1.users.user.utils import create_default_superuser
    async with DBConfigurer.Session() as session:
        get_user_db_context = contextlib.asynccontextmanager(get_user_db)
        async with get_user_db_context(session) as user_db:
            get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)
            async with get_user_manager_context(user_db) as user_manager:
                await create_default_superuser(
                    session=session,
                    user_manager=user_manager
                )


if __name__ == "__main__":
    asyncio.run(main())
