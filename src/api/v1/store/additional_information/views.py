from decimal import Decimal
from typing import Optional, TYPE_CHECKING, Dict, Any

from fastapi import APIRouter, status, Request, Query, Depends, Form
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer, RateLimiter
from src.scripts.pagination import paginate_result
from .schemas import (
    AddInfoShort,
    AddInfoRead,
)
from .service import AddInfoService
from .filters import AddInfoFilter, AddInfoFilterComplex
from . import dependencies as deps
from ..products.schemas import ProductShort
from src.api.v1.users.user.dependencies import current_superuser

if TYPE_CHECKING:
    from src.core.models import (
        AdditionalInformation,
    )


RELATIONS_LIST = [
    {
        "name": "product",
        "usage": "/{id}/product",
        "conditions": "public"
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
    from src.scripts.get_routes import get_routes as scrypt_get_routes
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
    response_model=list[AddInfoShort],
    status_code=status.HTTP_200_OK,
    description="Get the list of the all items (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
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


# 4
@router.get(
    "/full",
    dependencies=[Depends(current_superuser),],
    response_model=list[AddInfoRead],
    status_code=status.HTTP_200_OK,
    description="Get the list of the all items with product relations (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: AddInfoFilterComplex = FilterDepends(AddInfoFilterComplex),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: AddInfoService = AddInfoService(
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
    status_code=status.HTTP_200_OK,
    response_model=AddInfoShort,
    description="Get the additional info of the product by product_id"
)
@RateLimiter.rate_limit()
async def get_one(
        request: Request,
        product_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: AddInfoService = AddInfoService(
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
    response_model=AddInfoRead,
    description="Get the additional info of the product by product_id with all relations (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_complex(
        request: Request,
        product_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: AddInfoService = AddInfoService(
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
    response_model=AddInfoRead,
    description="Create additional info for existing product (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def create_one(
        request: Request,
        product_id: int = Form(),
        weight: Optional[Decimal] = Form(decimal_places=2, default=None),
        size: Optional[str] = Form(default=None),
        guarantee: Optional[str] = Form(default=None),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> AddInfoRead:

    service: AddInfoService = AddInfoService(
        session=session
    )
    return await service.create_one(
        product_id=product_id,
        weight=weight,
        size=size,
        guarantee=guarantee,
    )


# 8
@router.delete(
    "/{product_id}",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete additional info of the product by product_id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def delete_one(
        request: Request,
        orm_model: "AdditionalInformation" = Depends(deps.get_one),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: AddInfoService = AddInfoService(
        session=session
    )
    return await service.delete_one(orm_model)


# 9
@router.put(
    "",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=AddInfoRead,
    description="Edit additional info for existing product (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def edit_one(
        request: Request,
        orm_model: "AdditionalInformation" = Depends(deps.get_one),
        product_id: int = Form(),
        weight: Optional[Decimal] = Form(decimal_places=2, default=None),
        size: Optional[str] = Form(default=None),
        guarantee: Optional[str] = Form(default=None),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> AddInfoRead:

    service: AddInfoService = AddInfoService(
        session=session
    )
    return await service.edit_one(
        orm_model=orm_model,
        product_id=product_id,
        weight=weight,
        size=size,
        guarantee=guarantee,
    )


# 10
@router.patch(
    "",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=AddInfoRead,
    description="Edit additional info for existing product (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def edit_one_partial(
        request: Request,
        orm_model: "AdditionalInformation" = Depends(deps.get_one),
        product_id: Optional[int] = Form(default=None),
        weight: Optional[Decimal] = Form(decimal_places=2, default=None),
        size: Optional[str] = Form(default=None),
        guarantee: Optional[str] = Form(default=None),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> AddInfoRead:

    service: AddInfoService = AddInfoService(
        session=session
    )
    return await service.edit_one(
        orm_model=orm_model,
        product_id=product_id,
        weight=weight,
        size=size,
        guarantee=guarantee,
        is_partial=True,
    )


# 11
@router.get(
    "/{product_id}/product",
    status_code=status.HTTP_200_OK,
    response_model=ProductShort,
    description="Get the relations product of additional info by product_id"
)
@RateLimiter.rate_limit()
async def get_one(
        request: Request,
        product_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: AddInfoService = AddInfoService(
        session=session
    )
    return await service.get_one_complex(
        product_id=product_id,
        maximized=False,
        relations=['product']
    )
