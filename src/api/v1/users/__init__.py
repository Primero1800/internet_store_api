from fastapi import APIRouter

from .user import router as user_router
from .usertools import router as usertools_router


from src.core.settings import settings


router = APIRouter()


router.include_router(
    user_router,
    prefix=settings.tags.USERS_PREFIX,
    tags=[settings.tags.USERS_TAG]
)


router.include_router(
    usertools_router,
    prefix=settings.tags.USERTOOLS_PREFIX,
    tags=[settings.tags.USERTOOLS_TAG]
)
