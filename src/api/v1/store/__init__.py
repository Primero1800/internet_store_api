from fastapi import APIRouter

from src.core.settings import settings

from .brands import router as brands_router
from .rubrics import router as rubrics_router


router = APIRouter()

router.include_router(
    brands_router,
    prefix=settings.tags.BRANDS_PREFIX,
    tags=[settings.tags.BRANDS_TAG,],
)


router.include_router(
    rubrics_router,
    prefix=settings.tags.RUBRICS_PREFIX,
    tags=[settings.tags.RUBRICS_TAG,],
)