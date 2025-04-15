from typing import TYPE_CHECKING, List, Optional

from fastapi import (
    APIRouter,
    UploadFile,
    Form,
    File,
    Depends,
    status,
    Request,
    Query,
)
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.scrypts.pagination import paginate_result
from .service import ProductsService
from .schemas import (
    ProductRead,
    ProductShort,
)
from .filters import ProductFilter
from src.api.v1.users.dependencies import current_superuser
from src.core.config import DBConfigurer, RateLimiter
from . import dependencies as deps

if TYPE_CHECKING:
    from src.core.models import Product


router = APIRouter()


@router.get(
    "/",
    response_model=List[ProductShort],
    status_code=status.HTTP_200_OK,
)
@RateLimiter.rate_limit()
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: ProductFilter = FilterDepends(ProductFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: ProductsService = ProductsService(
        session=session
    )
    result_full = await service.get_all(filter_model=filter_model)
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


@router.get(
    "/full/",
    dependencies=[Depends(current_superuser),],
    response_model=List[ProductRead],
    status_code=status.HTTP_200_OK,
)
@RateLimiter.rate_limit()
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: ProductFilter = FilterDepends(ProductFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: ProductsService = ProductsService(
        session=session
    )
    result_full = await service.get_all_full(filter_model=filter_model)
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )
