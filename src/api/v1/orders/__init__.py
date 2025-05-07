from fastapi import APIRouter

from src.core.settings import settings

from .order import router as order_router
from .person import router as person_router
from .address import router as address_router


router = APIRouter()


router.include_router(
    order_router,
    tags=[settings.tags.ORDERS_TAG,],
    prefix=settings.tags.ORDERS_PREFIX
)


router.include_router(
    person_router,
    tags=[settings.tags.PERSONS_TAG,],
    prefix=settings.tags.PERSONS_PREFIX
)


router.include_router(
    address_router,
    tags=[settings.tags.ADDRESSES_TAG,],
    prefix=settings.tags.ADDRESSES_PREFIX
)
