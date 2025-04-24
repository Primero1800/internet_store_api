from decimal import Decimal
from typing import Optional, TYPE_CHECKING, Dict, Any

from fastapi import APIRouter, status, Request, Query, Depends, Form
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer, RateLimiter
from src.scrypts.pagination import paginate_result
from src.tools.stars_choices import StarsChoices
from .schemas import (
    SaleInfoShort,
    SaleInfoRead,
)
from .service import SaleInfoService
from .filters import SaleInfoFilter, SaleInfoFilterComplex
from . import dependencies as deps
from ..products.schemas import ProductShort
from ...users.dependencies import current_superuser

if TYPE_CHECKING:
    from src.core.models import (
        SaleInformation,
    )


RELATIONS_LIST = [
    {
        "name": "product",
        "usage": "/{id}/product",
        "conditions": "private"
    },
]

router = APIRouter()


# 1
@router.get(
    "/routes",
    status_code=status.HTTP_200_OK,
    description="Getting all the routes of the current branch",
)
@RateLimiter.rate_limit()
async def get_routes(
        request: Request,
) -> list[Dict[str, Any]]:
    from src.scrypts.get_routes import get_routes as scrypt_get_routes
    return await scrypt_get_routes(
        application=router,
        tags=False,
        desc=True
    )


# 2
@router.get(
    "/relations",
    status_code=status.HTTP_200_OK,
    description="Getting the relations info for the branch items"
)
@RateLimiter.rate_limit()
async def get_relations(
        request: Request,
) -> list[Dict[str, Any]]:
    return RELATIONS_LIST


# 3
@router.get(
    "",
    dependencies=[Depends(current_superuser)],
    response_model=list[SaleInfoShort],
    status_code=status.HTTP_200_OK,
    description="Get the list of the all items (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: SaleInfoFilter = FilterDepends(SaleInfoFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    result_full = await service.get_all(filter_model=filter_model)
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 4
@router.get(
    "/full",
    dependencies=[Depends(current_superuser),],
    response_model=list[SaleInfoRead],
    status_code=status.HTTP_200_OK,
    description="Get the list of the all items with product relations (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: SaleInfoFilterComplex = FilterDepends(SaleInfoFilterComplex),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    result_full = await service.get_all_full(filter_model=filter_model)
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 5
@router.get(
    "/{product_id}",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_200_OK,
    response_model=SaleInfoShort,
    description="Get item of the product by product_id"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one(
        request: Request,
        product_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.get_one(
        product_id=product_id
    )


# 6
@router.get(
    "/{product_id}/full",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_200_OK,
    response_model=SaleInfoRead,
    description="Get item of the product by product_id with all relations (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_complex(
        request: Request,
        product_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.get_one_complex(
        product_id=product_id
    )


# 7
@router.post(
    "",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=SaleInfoRead,
    description="Create item for existing product (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def create_one(
        request: Request,
        product_id: int = Form(),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> SaleInfoRead:

    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.create_one(
        product_id=product_id,
    )


# 8
@router.delete(
    "/{product_id}",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete item of the product by product_id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def delete_one(
        request: Request,
        orm_model: "SaleInformation" = Depends(deps.get_one),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.delete_one(orm_model)


# 9
@router.patch(
    "",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=SaleInfoRead,
    description="Edit item for existing product (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def edit_one_partial(
        request: Request,
        orm_model: "SaleInformation" = Depends(deps.get_one),
        product_id: Optional[int] = Form(default=None),
        viewed_count: Optional[int] = Form(default=None),
        sold_count: Optional[int] = Form(default=None),
        voted_count: Optional[int] = Form(default=None),
        rating_summary: Optional[Decimal] = Form(decimal_places=2, default=None),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> SaleInfoRead:

    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.edit_one(
        orm_model=orm_model,
        product_id=product_id,
        viewed_count=viewed_count,
        sold_count=sold_count,
        voted_count=voted_count,
        rating_summary=rating_summary,
        is_partial=True,
    )


# 10
@router.get(
    "/{product_id}/product",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=ProductShort,
    description="Get the relations product of sale info by product_id"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one(
        request: Request,
        product_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.get_one_complex(
        product_id=product_id,
        maximized=False,
        relations=['product']
    )


# 11
@router.post(
    "/get-or-create/{product_id}",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=SaleInfoShort,
    description="Get the sale info by product_id or creating empty one if not exists"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_or_create(
        request: Request,
        product_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.get_or_create(
        product_id=product_id,
    )


# 12_1
@router.post(
    "/do-vote/",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=list[SaleInfoShort],
    description="Change rating according votes"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def do_vote(
        request: Request,
        product_id_vote_add: Optional[int] = Form(default=None),
        vote_add: Optional[StarsChoices] = Form(default=None),
        product_id_vote_del: Optional[int] = Form(default=None),
        vote_del: Optional[StarsChoices] = Form(default=None),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.do_vote(
        product_id_vote_add=product_id_vote_add,
        vote_add=vote_add,
        product_id_vote_del=product_id_vote_del,
        vote_del=vote_del,
    )


# 12_2
@router.post(
    "/do-view/",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=SaleInfoShort,
    description="Increasing view_count on 1 (product viewing imitation)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def do_view(
        request: Request,
        product_id: int = Form(gt=0),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.do_view_or_sell(
        product_id=product_id
    )


# 12_3
@router.post(
    "/do-sell/",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=SaleInfoShort,
    description="Increasing sold_count on 1 (product selling imitation)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def do_sell(
        request: Request,
        product_id: int = Form(gt=0),
        count: Optional[int] = Form(default=1, gt=0),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.do_view_or_sell(
        action="sell",
        product_id=product_id,
        count=count
    )


