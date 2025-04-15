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
from .service import BrandsService
from .schemas import (
    BrandRead,
    BrandShort,
)
from .filters import BrandFilter
from src.api.v1.users.dependencies import current_superuser
from src.core.config import DBConfigurer, RateLimiter
from . import dependencies as deps

if TYPE_CHECKING:
    from src.core.models import Brand


router = APIRouter()


@router.get(
    "/",
    response_model=List[BrandShort],
    status_code=status.HTTP_200_OK,
)
@RateLimiter.rate_limit()
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: BrandFilter = FilterDepends(BrandFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: BrandsService = BrandsService(
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
    response_model=List[BrandRead],
    status_code=status.HTTP_200_OK,
)
@RateLimiter.rate_limit()
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: BrandFilter = FilterDepends(BrandFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: BrandsService = BrandsService(
        session=session
    )
    result_full = await service.get_all_full(filter_model=filter_model)
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


@router.get(
    "/title/{slug}/",
    status_code=status.HTTP_200_OK,
    response_model=BrandRead,
)
@RateLimiter.rate_limit()
async def get_one_by_slug(
        request: Request,
        slug: str,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: BrandsService = BrandsService(
        session=session
    )
    return await service.get_one_complex(
        slug=slug
    )


@router.get(
    "/{id}/",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=BrandRead,
)
@RateLimiter.rate_limit()
async def get_one(
        request: Request,
        id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: BrandsService = BrandsService(
        session=session
    )
    return await service.get_one_complex(
        id=id
    )


@router.post(
    "/",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=BrandRead,
)
@RateLimiter.rate_limit()
async def create_one(
        request: Request,
        title: str = Form(),
        description: str = Form(),
        image: UploadFile = File(),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):

    service: BrandsService = BrandsService(
        session=session
    )
    return await service.create_one(
        title=title,
        description=description,
        image_schema=image,
    )


@router.delete(
    "/{id}/",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_204_NO_CONTENT,
)
@RateLimiter.rate_limit()
async def delete_one(
        request: Request,
        orm_model: "Brand" = Depends(deps.get_one_simple),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: BrandsService = BrandsService(
        session=session
    )
    return await service.delete_one(orm_model)


@router.put(
        "/{id}/",
        dependencies=[Depends(current_superuser), ],
        status_code=status.HTTP_200_OK,
        response_model=BrandRead
)
@RateLimiter.rate_limit()
async def put_one(
        request: Request,
        title: str = Form(),
        description: str = Form(),
        image: UploadFile = File(),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        orm_model: "Brand" = Depends(deps.get_one_simple)
):
    service: BrandsService = BrandsService(
        session=session
    )
    return await service.edit_one(
        title=title,
        description=description,
        image_schema=image,
        orm_model=orm_model,
    )


@router.patch(
        "/{id}/",
        dependencies=[Depends(current_superuser), ],
        status_code=status.HTTP_200_OK,
        response_model=BrandRead
)
@RateLimiter.rate_limit()
async def patch_one(
        request: Request,
        title: Optional[str] = Form(default=None),
        description: Optional[str] = Form(default=None),
        image: Optional[UploadFile] = File(default=None),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        orm_model: "Brand" = Depends(deps.get_one_simple)
):
    service: BrandsService = BrandsService(
        session=session
    )
    return await service.edit_one(
        title=title,
        description=description,
        image_schema=image,
        orm_model=orm_model,
        is_partial=True
    )
