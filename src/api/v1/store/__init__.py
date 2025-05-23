from fastapi import APIRouter

from src.core.settings import settings

from .brands import router as brands_router
from .rubrics import router as rubrics_router
from .products import router as products_router
from .additional_information import router as add_info_router
from .sale_information import router as sale_info_router
from .votes import router as votes_router


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


router.include_router(
    products_router,
    prefix=settings.tags.PRODUCTS_PREFIX,
    tags=[settings.tags.PRODUCTS_TAG,],
)


router.include_router(
    add_info_router,
    prefix=settings.tags.ADD_INFO_PREFIX,
    tags=[settings.tags.ADD_INFO_TAG,],
)


router.include_router(
    sale_info_router,
    prefix=settings.tags.SALE_INFO_PREFIX,
    tags=[settings.tags.SALE_INFO_TAG,],
)


router.include_router(
    votes_router,
    prefix=settings.tags.VOTES_PREFIX,
    tags=[settings.tags.VOTES_TAG,],
)
