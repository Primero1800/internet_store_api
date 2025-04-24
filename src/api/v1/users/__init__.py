from fastapi import APIRouter

from src.api.v1.users.user.views import router as user_router


from src.core.settings import settings


router = APIRouter()


router.include_router(
    user_router,
    prefix=settings.tags.USERS_PREFIX,
    tags=[settings.tags.USERS_TAG]
)
