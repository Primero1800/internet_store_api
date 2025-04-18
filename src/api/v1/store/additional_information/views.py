from decimal import Decimal
from typing import Optional, TYPE_CHECKING, Dict, Any

from fastapi import APIRouter, status, Request, Query, Depends, Form
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer, RateLimiter
from src.scrypts.pagination import paginate_result
from .schemas import (
    AddInfoShort,
    AddInfoRead,
    AddInfoCreate,
    AddInfoUpdate,
    AddInfoPartialUpdate,
)
from .service import AddInfoService
from .filters import AddInfoFilter, AddInfoFilterComplex
from . import dependencies as deps
from ...users.dependencies import current_superuser

if TYPE_CHECKING:
    from src.core.models import (
        AdditionalInformation,
    )


router = APIRouter()


@router.get(
    "/routes",
    status_code=status.HTTP_200_OK,
    description="Getting all routes of current branch",
)
@RateLimiter.rate_limit()
async def get_routes(
        request: Request,
) -> Dict[str, Any]:
    from src.scrypts.get_routes import get_routes as scrypt_get_routes
    return await scrypt_get_routes(
        application=router,
        tags=False,
        deps=True,
        desc=True
    )


# @router.get(
#     "",
#     dependencies=[Depends(current_superuser)],
#     response_model=list[AddInfoShort],
#     status_code=status.HTTP_200_OK,
# )
# @RateLimiter.rate_limit()
# async def get_all(
#         request: Request,
#         page: int = Query(1, gt=0),
#         size: int = Query(10, gt=0),
#         filter_model: AddInfoFilter = FilterDepends(AddInfoFilter),
#         session: AsyncSession = Depends(DBConfigurer.session_getter)
# ):
#     service: AddInfoService = AddInfoService(
#         session=session
#     )
#     result_full = await service.get_all(filter_model=filter_model)
#     return await paginate_result(
#         query_list=result_full,
#         page=page,
#         size=size,
#     )
#
#
# @router.get(
#     "/product/{id}",
#     status_code=status.HTTP_200_OK,
#     response_model=AddInfoRead,
# )
# @RateLimiter.rate_limit()
# async def get_one(
#         request: Request,
#         product_id: int,
#         session: AsyncSession = Depends(DBConfigurer.session_getter)
# ):
#     service: AddInfoService = AddInfoService(
#         session=session
#     )
#     return await service.get_one_complex(
#         product_id=product_id
#     )
#
#
# @router.get(
#     "/full",
#     dependencies=[Depends(current_superuser),],
#     response_model=list[AddInfoRead],
#     status_code=status.HTTP_200_OK,
# )
# @RateLimiter.rate_limit()
# async def get_all_full(
#         request: Request,
#         page: int = Query(1, gt=0),
#         size: int = Query(10, gt=0),
#         filter_model: AddInfoFilterComplex = FilterDepends(AddInfoFilterComplex),
#         session: AsyncSession = Depends(DBConfigurer.session_getter)
# ):
#     service: AddInfoService = AddInfoService(
#         session=session
#     )
#     result_full = await service.get_all_full(filter_model=filter_model)
#     return await paginate_result(
#         query_list=result_full,
#         page=page,
#         size=size,
#     )
#
#
# @router.get(
#     "/{id}",
#     dependencies=[Depends(current_superuser), ],
#     status_code=status.HTTP_200_OK,
#     response_model=AddInfoRead,
# )
# @RateLimiter.rate_limit()
# async def get_one(
#         request: Request,
#         id: int,
#         session: AsyncSession = Depends(DBConfigurer.session_getter)
# ):
#     service: AddInfoService = AddInfoService(
#         session=session
#     )
#     return await service.get_one_complex(
#         id=id
#     )
#
#
# @router.post(
#     "",
#     dependencies=[Depends(current_superuser),],
#     status_code=status.HTTP_201_CREATED,
#     response_model=AddInfoRead,
# )
# @RateLimiter.rate_limit()
# async def create_one(
#         request: Request,
#         product_id: int = Form(),
#         weight: Optional[Decimal] = Form(decimal_places=2, default=None),
#         size: Optional[str] = Form(default=None),
#         guarantee: Optional[str] = Form(default=None),
#         session: AsyncSession = Depends(DBConfigurer.session_getter)
# ) -> AddInfoRead:
#
#     service: AddInfoService = AddInfoService(
#         session=session
#     )
#     return await service.create_one(
#         product_id=product_id,
#         weight=weight,
#         size=size,
#         guarantee=guarantee,
#     )
#
#
# @router.delete(
#     "/product/{id}",
#     dependencies=[Depends(current_superuser), ],
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# @RateLimiter.rate_limit()
# async def delete_one(
#         request: Request,
#         orm_model: "AdditionalInformation" = Depends(deps.get_one_simple_by_product_id),
#         session: AsyncSession = Depends(DBConfigurer.session_getter),
# ):
#     service: AddInfoService = AddInfoService(
#         session=session
#     )
#     return await service.delete_one(orm_model)
