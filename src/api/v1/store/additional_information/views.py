from fastapi import APIRouter, status, Request, Query, Depends
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer, RateLimiter
from src.scrypts.pagination import paginate_result
from .schemas import (
    AddInfoShort,
    AddInfoRead,
    AddInfoCreate,
    AddInfoUpdate,
    AddInfoUpdatePartial,
)
from .service import AddInfoService
from .filters import AddInfoFilter
from ...users.dependencies import current_superuser

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(current_superuser)],
    response_model=list[AddInfoShort],
    status_code=status.HTTP_200_OK,
)
@RateLimiter.rate_limit()
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: AddInfoFilter = FilterDepends(AddInfoFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: AddInfoService = AddInfoService(
        session=session
    )
    result_full = await service.get_all(filter_model=filter_model)
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )
