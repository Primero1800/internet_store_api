from fastapi import APIRouter

from src.core.settings import settings

from .brands import router as brands_router


router = APIRouter()

router.include_router(
    brands_router,
    prefix=settings.tags.BRANDS_PREFIX,
    tags=[settings.tags.BRANDS_TAG,],
)