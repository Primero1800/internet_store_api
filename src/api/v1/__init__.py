from fastapi import APIRouter

from .users import router as users_router
from src.core.settings import settings


router = APIRouter()

router.include_router(
    users_router,
    prefix=settings.tags.USERS_PREFIX,
    tags=[settings.tags.USERS_TAG]
)