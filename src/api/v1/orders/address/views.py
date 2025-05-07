from typing import TYPE_CHECKING, List, Optional, Dict, Any, Union

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

from src.core.sessions.fastapi_sessions_config import cookie_or_none, verifier_or_none
from src.scrypts.pagination import paginate_result
from .service import AddressesService
from .schemas import (
    AddressRead,
    AddressShort,
)
from .filters import AddressFilter
from src.api.v1.users.user.dependencies import current_superuser, current_user_or_none
from src.core.config import DBConfigurer, RateLimiter
from . import dependencies as deps
from . import utils

if TYPE_CHECKING:
    from src.core.models import(
        User,
        Address,
    )
    from src.api.v1.orders.address.session_address import SessionAddress
    from src.core.sessions.fastapi_sessions_config import SessionData


RELATIONS_LIST = [
    {
        "name": "user",
        "usage": "/me-session/user",
        "conditions": "public"
    },
    {
        "name": "user",
        "usage": "/{user_id}/user",
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
    dependencies=[Depends(current_superuser),],
    response_model=List[AddressShort],
    status_code=status.HTTP_200_OK,
    description="Get items list"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        for_registered_users: Optional[bool] = Query(default=None, description="Filter addresses of registered users"),
        filter_model: AddressFilter = FilterDepends(AddressFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: AddressesService = AddressesService(
        session=session
    )
    result_full = await service.get_all(
        filter_model=filter_model,
        db_addresses=for_registered_users,
    )
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 4
@router.get(
    "/full",
    dependencies=[Depends(current_superuser),],
    response_model=List[AddressRead],
    status_code=status.HTTP_200_OK,
    description="Get full items list (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        for_registered_users: Optional[bool] = Query(default=None, description="Filter addresses of registered users"),
        filter_model: AddressFilter = FilterDepends(AddressFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: AddressesService = AddressesService(
        session=session
    )
    result_full = await service.get_all_full(
        filter_model=filter_model,
        db_addresses=for_registered_users,
    )
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 5_1
@router.get(
    "/me-session",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(cookie_or_none),],
    response_model=AddressShort,
    description="Get personal item"
)
@RateLimiter.rate_limit()
async def get_one_of_me(
        request: Request,
        orm_model: Union["Address", "SessionAddress"] = Depends(deps.get_one_session),
):
    return await utils.get_short_schema_from_orm(orm_model)


# 5_2
@router.get(
    "/{user_id}",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_200_OK,
    response_model=AddressShort,
    description="Get item by user_id"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: AddressesService = AddressesService(
        session=session
    )
    return await service.get_one(
        user_id=user_id,
    )


# 6_1
@router.get(
    "/me-session/full",
    dependencies=[Depends(cookie_or_none),],
    status_code=status.HTTP_200_OK,
    response_model=AddressRead,
    description="Get personal item full"
)
@RateLimiter.rate_limit()
async def get_one_full_of_me_session(
        request: Request,
        orm_model: Union["Address", "SessionAddress"] = Depends(deps.get_one_session_full),
):
    return await utils.get_schema_from_orm(orm_model)


# 6_2
@router.get(
    "/{user_id}/full",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=AddressRead,
    description="Get full item by user_id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_full(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: AddressesService = AddressesService(
        session=session
    )
    return await service.get_one_complex(
        user_id=user_id,
        maximized=True
    )


# 7
@router.post(
    "",
    dependencies=[Depends(cookie_or_none),],
    status_code=status.HTTP_201_CREATED,
    response_model=AddressRead,
    description="Create one personal item"
)
@RateLimiter.rate_limit()
async def create_one(
        request: Request,

        address: str = Form(min_length=6, max_length=100),
        city: str = Form(min_length=2, max_length=50),
        postcode: Optional[str] = Form(max_length=16, default=None),
        email: Optional[str] = Form(min_length=6, max_length=320, default=None),
        phonenumber: str = Form(min_length=5, max_length=20),

        user: "User" = Depends(current_user_or_none),
        session_data: "SessionData" = Depends(verifier_or_none),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):

    service: AddressesService = AddressesService(
        session=session,
        session_data=session_data
    )
    return await service.create_one(
        user=user,
        address=address,
        city=city,
        postcode=postcode,
        email=email,
        phonenumber=phonenumber,
    )


# 8
@router.delete(
    "/{user_id}",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete item by user_id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def delete_one(
        request: Request,
        orm_model: "Address" = Depends(deps.get_one_simple),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: AddressesService = AddressesService(
        session=session
    )
    return await service.delete_one(
        orm_model=orm_model,
    )


# 9
@router.patch(
        "/me-session",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(cookie_or_none),],
        response_model=AddressRead,
        description="Partial edit personal item"
)
@RateLimiter.rate_limit()
async def patch_one(
        request: Request,

        address: Optional[str] = Form(min_length=6, max_length=100, default=None),
        city:Optional[str] = Form(min_length=2, max_length=50, default=None),
        postcode: Optional[str] = Form(max_length=16, default=None),
        email: Optional[str] = Form(min_length=6, max_length=320, default=None),
        phonenumber: Optional[str] = Form(min_length=5, max_length=20, default=None),

        orm_model: Union["Address", "SessionAddress"] = Depends(deps.get_one_session),
        session_data: "SessionData" = Depends(verifier_or_none),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: AddressesService = AddressesService(
        session=session,
        session_data=session_data
    )
    return await service.edit_one(
        orm_model=orm_model,
        address=address,
        city=city,
        postcode=postcode,
        email=email,
        phonenumber=phonenumber,
        is_partial=True
    )


# 10_1
@router.get(
        "/me-session/user",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(cookie_or_none), ],
        description="Get personal item's relation 'user'"
)
@RateLimiter.rate_limit()
async def get_personal_relations_user(
        request: Request,
        orm_model: Union["Address", "SessionAddress"] = Depends(deps.get_one_session_full),
):
    return await utils.get_schema_from_orm(
        orm_model=orm_model,
        relations=['user',],
    )


# 10_2
@router.get(
        "/{user_id}/user",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(current_superuser), ],
        description="Get item's relation 'user' by user_id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_relations_user_by_user_id(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: AddressesService = AddressesService(
        session=session,
    )
    return await service.get_one_complex(
        user_id=user_id,
        relations=['user',]
    )
