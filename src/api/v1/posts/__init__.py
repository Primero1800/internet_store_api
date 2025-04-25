from fastapi import APIRouter

from src.core.settings import settings
from .post import router as post_router


router = APIRouter()


router.include_router(
    post_router,
    prefix=settings.tags.POSTS_PREFIX,
    tags=[settings.tags.POSTS_TAG]
)
