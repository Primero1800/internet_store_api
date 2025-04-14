from typing import TYPE_CHECKING, List, Optional

from fastapi import (
    APIRouter,
    UploadFile,
    Form,
    File,
    Depends,
    HTTPException,
    status,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .service import BrandsService
from .schemas import (
    BrandCreate, BrandRead, BrandUpdate, BrandPartialUpdate, BrandShort,
)
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
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: BrandsService = BrandsService(
        session=session
    )
    return await service.get_all()


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


@router.get(
    "/full/",
    dependencies=[Depends(current_superuser),],
    response_model=List[BrandRead],
    status_code=status.HTTP_200_OK,
)
@RateLimiter.rate_limit()
async def get_all_full(
        request: Request,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: BrandsService = BrandsService(
        session=session
    )
    return await service.get_all_full()


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









# @router.put(
#     "/{id}/",
#     dependencies=[Depends(current_superuser), ],
#     status_code=status.HTTP_200_OK,
#     response_model=BrandRead
# )
# async def edit_one(
#     title: str = Form(),
#     description: str = Form(),
#     image: UploadFile = File(),
#     session: AsyncSession = Depends(DBConfigurer.session_getter),
#     orm_model: "Brand" = Depends(deps.get_one_simple)
# ):
#
#     # catching ValidationError in exception_handler
#     instance: BrandUpdate = BrandUpdate(title=title, description=description)
#
#     try:
#         orm_model: "Brand" = await crud.edit_one(
#             orm_model=orm_model,
#             instance=instance,
#             image_schema=image,
#             session=session,
#         )
#         return await utils.get_schema_from_orm(orm_model=orm_model)
#     except (CustomException, Exception) as exc:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=exc.msg if hasattr(exc, "msg") else str(exc)
#         )
#
#
# @router.patch(
#     "/{id}/",
#     dependencies=[Depends(current_superuser), ],
#     status_code=status.HTTP_200_OK,
#     response_model=BrandRead
# )
# async def edit_one_partial(
#     title: Optional[str] = Form(default=None),
#     description: Optional[str] = Form(default=None),
#     image: Optional[UploadFile] = File(default=None),
#     session: AsyncSession = Depends(DBConfigurer.session_getter),
#     orm_model: "Brand" = Depends(deps.get_one_simple)
# ):
#
#     # catching ValidationError in exception_handler
#     instance: BrandPartialUpdate = BrandPartialUpdate(title=title, description=description)
#
#     try:
#         orm_model: "Brand" = await crud.edit_one(
#             orm_model=orm_model,
#             instance=instance,
#             image_schema=image,
#             session=session,
#             is_partial=True,
#         )
#         return await utils.get_schema_from_orm(orm_model=orm_model)
#     except (CustomException, Exception) as exc:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=exc.msg if hasattr(exc, "msg") else str(exc)
#         )