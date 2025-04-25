from typing import TYPE_CHECKING, List, Optional, Dict, Any

from fastapi import (
    APIRouter,
    Form,
    Depends,
    status,
    Request,
    Query,
)
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.scrypts.pagination import paginate_result
from src.tools.stars_choices import StarsChoices
from .service import VotesService
from .schemas import (
    VoteRead,
    VoteShort,
)
from .filters import VoteFilter
from src.api.v1.users.user.dependencies import current_superuser, current_user
from src.core.config import DBConfigurer, RateLimiter
from ..products.schemas import ProductShort
from src.api.v1.users.user.schemas import UserPublicExtended
from . import dependencies as deps

if TYPE_CHECKING:
    from src.core.models import(
        User,
        Vote,
    )


RELATIONS_LIST = [
    {
        "name": "user",
        "usage": "/{id}/user",
        "conditions": "private"
    },
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
    response_model=List[VoteShort],
    status_code=status.HTTP_200_OK,
    description="Get items list"
)
@RateLimiter.rate_limit()
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: VoteFilter = FilterDepends(VoteFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: VotesService = VotesService(
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
    response_model=List[VoteRead],
    status_code=status.HTTP_200_OK,
    description="Get full items list (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: VoteFilter = FilterDepends(VoteFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: VotesService = VotesService(
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
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=VoteShort,
    description="Get item by id"
)
@RateLimiter.rate_limit()
async def get_one(
        request: Request,
        id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: VotesService = VotesService(
        session=session
    )
    return await service.get_one(
        id=id,
    )


# 6
@router.get(
    "/{id}/full",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=VoteRead,
    description="Get full item by id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_full(
        request: Request,
        id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: VotesService = VotesService(
        session=session
    )
    return await service.get_one_complex(
        id=id,
        maximized=True
    )


# 7
@router.post(
    "",
    dependencies=[Depends(current_user),],
    status_code=status.HTTP_201_CREATED,
    response_model=VoteRead,
    description="Create one item (for superuser only)"
)
@RateLimiter.rate_limit()
async def create_one(
        request: Request,
        product_id: int = Form(),
        name: str = Form(),
        review: Optional[str] = Form(default=None),
        stars: StarsChoices = Form(default=StarsChoices.S5),
        user: "User" = Depends(current_user),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):

    service: VotesService = VotesService(
        session=session
    )
    return await service.create_one(
        user=user,
        product_id=product_id,
        name=name,
        review=review,
        stars=stars,
    )


# 8
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete item by id (for superuser and item's author only)"
)
@RateLimiter.rate_limit()
async def delete_one(
        request: Request,
        user: "User" = Depends(current_user),
        orm_model: "Vote" = Depends(deps.get_one_simple),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: VotesService = VotesService(
        session=session
    )
    return await service.delete_one(
        orm_model=orm_model,
        user=user
    )


# 9
@router.put(
        "/{id}",
        status_code=status.HTTP_200_OK,
        response_model=VoteRead,
        description="Edit item by id (for superuser and item's author only)"
)
@RateLimiter.rate_limit()
async def put_one(
        request: Request,
        user: "User" = Depends(current_user),
        orm_model: "Vote" = Depends(deps.get_one_simple),
        product_id: int = Form(),
        name: str = Form(),
        review: Optional[str] = Form(default=None),
        stars: StarsChoices = Form(default=StarsChoices.S5),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: VotesService = VotesService(
        session=session
    )
    return await service.edit_one(
        orm_model=orm_model,
        user=user,
        product_id=product_id,
        name=name,
        review=review,
        stars=stars,
    )


# 10
@router.patch(
        "/{id}",
        status_code=status.HTTP_200_OK,
        response_model=VoteRead,
        description="Partial edit item by id (for superuser and item's author only)"
)
@RateLimiter.rate_limit()
async def patch_one(
        request: Request,
        user: "User" = Depends(current_user),
        orm_model: "Vote" = Depends(deps.get_one_simple),
        product_id: Optional[int] = Form(default=None),
        name: Optional[str] = Form(default=None),
        review: Optional[str] = Form(default=None),
        stars: Optional[StarsChoices] = Form(default=None),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: VotesService = VotesService(
        session=session
    )
    return await service.edit_one(
        orm_model=orm_model,
        user=user,
        product_id=product_id,
        name=name,
        review=review,
        stars=stars,
        is_partial=True
    )


# 11_1
@router.get(
    "/{id}/user",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_200_OK,
    response_model=UserPublicExtended,
    description="Get item relations user by id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_relations_user(
        request: Request,
        id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: VotesService = VotesService(
        session=session
    )
    return await service.get_one_complex(
        id=id,
        maximized=False,
        relations=['user',]
    )


# 11_2
@router.get(
    "/{id}/product",
    status_code=status.HTTP_200_OK,
    description="Get item relations product by id"
)
@RateLimiter.rate_limit()
async def get_relations_product(
        request: Request,
        id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> ProductShort | None:
    service: VotesService = VotesService(
        session=session
    )
    return await service.get_one_complex(
        id=id,
        maximized=False,
        relations=['product',]
    )
