from fastapi import APIRouter

from src.api.v1.users import router as users_router
from .auth import router as auth_router
from .sessions import router as sessions_router
from .store import router as store_router
from .posts import router as posts_router
from .carts import router as carts_router
from .orders import router as orders_router


from src.core.settings import settings


router = APIRouter()

router.include_router(
    auth_router,
    prefix=settings.tags.AUTH_PREFIX,
    tags=[settings.tags.AUTH_TAG]
)


router.include_router(
    users_router,
)


router.include_router(
    sessions_router,
    prefix=settings.tags.SESSIONS_PREFIX,
    tags=[settings.tags.SESSIONS_TAG]
)

router.include_router(
    store_router,
)

router.include_router(
    posts_router,
)

router.include_router(
    carts_router,
    prefix=settings.tags.CARTS_PREFIX,
    tags=[settings.tags.CARTS_TAG]
)

router.include_router(
    orders_router,
)
