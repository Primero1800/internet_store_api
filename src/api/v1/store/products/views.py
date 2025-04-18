from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional, Any

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
from src.tools.discount_choices import DiscountChoices
from .service import ProductsService
from .schemas import (
    ProductRead,
    ProductReadPublic,
    ProductShort,
)
from .filters import ProductFilter
from src.api.v1.users.dependencies import current_superuser
from src.core.config import DBConfigurer, RateLimiter
from . import dependencies as deps


if TYPE_CHECKING:
    from src.core.models import (
        Product,
        Brand,
    )


router = APIRouter()


@router.get(
    "",
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
    "/full",
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


@router.get(
    "/title/{slug}",
    status_code=status.HTTP_200_OK,
    response_model=ProductReadPublic,
)
@RateLimiter.rate_limit()
async def get_one_by_slug(
        request: Request,
        slug: str,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: ProductsService = ProductsService(
        session=session
    )
    return await service.get_one_complex(
        slug=slug
    )


@router.get(
    "/{id}",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=ProductRead,
)
@RateLimiter.rate_limit()
async def get_one(
        request: Request,
        id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: ProductsService = ProductsService(
        session=session
    )
    return await service.get_one_complex(
        id=id
    )


@router.post(
    "",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=ProductRead,
)
@RateLimiter.rate_limit()
async def create_one(
        request: Request,
        title: str = Form(),
        description: str = Form(),
        brand_id: int = Form(),
        start_price: Decimal = Form(decimal_places=2),
        available: bool = Form(),
        discount: DiscountChoices = Form(),
        quantity: int = Form(),
        rubric_ids: list[Any] = Form(),
        images: List[UploadFile] = File(),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> ProductRead:

    service: ProductsService = ProductsService(
        session=session
    )
    return await service.create_one(
        title=title,
        description=description,
        brand_id=brand_id,
        start_price=start_price,
        available=available,
        discount=discount,
        quantity=quantity,
        rubric_ids=rubric_ids,
        image_schemas=images,
    )


@router.delete(
    "/{id}",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_204_NO_CONTENT,
)
@RateLimiter.rate_limit()
async def delete_one(
        request: Request,
        orm_model: "Product" = Depends(deps.get_one_simple),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: ProductsService = ProductsService(
        session=session
    )
    return await service.delete_one(orm_model)


@router.put(
        "/{id}",
        dependencies=[Depends(current_superuser), ],
        status_code=status.HTTP_200_OK,
        response_model=ProductRead
)
@RateLimiter.rate_limit()
async def put_one(
        request: Request,
        title: str = Form(),
        description: str = Form(),
        brand_id: int = Form(),
        start_price: Decimal = Form(decimal_places=2),
        available: bool = Form(),
        discount: DiscountChoices = Form(),
        quantity: int = Form(),
        rubric_ids: list[Any] = Form(),
        images: List[UploadFile] = File(),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        orm_model: "Product" = Depends(deps.get_one_complex)
):
    service: ProductsService = ProductsService(
        session=session
    )
    return await service.edit_one(
        orm_model=orm_model,
        title=title,
        description=description,
        brand_id=brand_id,
        start_price=start_price,
        available=available,
        discount=discount,
        quantity=quantity,
        rubric_ids=rubric_ids,
        image_schemas=images,
    )


@router.patch(
        "/{id}",
        dependencies=[Depends(current_superuser), ],
        status_code=status.HTTP_200_OK,
        response_model=ProductRead
)
@RateLimiter.rate_limit()
async def patch_one(
        request: Request,
        title: Optional[str] = Form(default=None),
        description: Optional[str] = Form(default=None),
        brand_id: Optional[int] = Form(default=None),
        start_price: Optional[Decimal] = Form(decimal_places=2, default=None),
        available: Optional[bool] = Form(default=None),
        discount: Optional[DiscountChoices] = Form(default=None),
        quantity: Optional[int] = Form(default=None),
        rubric_ids: Optional[list[Any]] = Form(default=None),
        images: Optional[List[UploadFile]] = None,
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        orm_model: "Product" = Depends(deps.get_one_complex)
):
    service: ProductsService = ProductsService(
        session=session
    )
    return await service.edit_one(
        orm_model=orm_model,
        title=title,
        description=description,
        brand_id=brand_id,
        start_price=start_price,
        available=available,
        discount=discount,
        quantity=quantity,
        rubric_ids=rubric_ids,
        image_schemas=images,
        is_partial=True
    )
