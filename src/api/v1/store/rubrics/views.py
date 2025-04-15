from typing import List

from fastapi import (
    APIRouter,
    status,
    Request,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .service import RubricsService
from src.core.config import RateLimiter, DBConfigurer
from .schemas import (
    RubricShort,
    RubricRead,
)


router = APIRouter()


@router.get(
    "/",
    response_model=List[RubricShort],
    status_code=status.HTTP_200_OK,
)
@RateLimiter.rate_limit()
async def get_all(
        request: Request,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: RubricsService = RubricsService(
        session=session
    )
    return await service.get_all()


@router.get(
    "/title/{slug}/",
    status_code=status.HTTP_200_OK,
    response_model=RubricRead,
)
@RateLimiter.rate_limit()
async def get_one_by_slug(
        request: Request,
        slug: str,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: RubricsService = RubricsService(
        session=session
    )
    return await service.get_one_complex(
        slug=slug
    )
