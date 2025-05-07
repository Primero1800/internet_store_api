from typing import TYPE_CHECKING, List, Optional, Dict, Any, Union

from fastapi import (
    APIRouter,
    Form,
    Depends,
    status,
    Request,
    Query, Body,
)
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.sessions.fastapi_sessions_config import cookie_or_none, verifier_or_none
from src.scrypts.pagination import paginate_result
from .service import PersonsService
from .schemas import (
    PersonRead,
    PersonShort,
)
from .filters import PersonFilter
from src.api.v1.users.user.dependencies import current_superuser, current_user_or_none
from src.core.config import DBConfigurer, RateLimiter
from src.api.v1.users.user.schemas import UserPublicExtended
from . import dependencies as deps
from . import utils

if TYPE_CHECKING:
    from src.core.models import(
        User,
        Person,
    )
    from src.api.v1.orders.person.session_person import SessionPerson
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
    response_model=List[PersonShort],
    status_code=status.HTTP_200_OK,
    description="Get items list"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        for_registered_users: Optional[bool] = Query(default=None, description="Filter persons of registered users"),
        filter_model: PersonFilter = FilterDepends(PersonFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: PersonsService = PersonsService(
        session=session
    )
    result_full = await service.get_all(
        filter_model=filter_model,
        db_persons=for_registered_users,
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
    response_model=List[PersonRead],
    status_code=status.HTTP_200_OK,
    description="Get full items list (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        for_registered_users: Optional[bool] = Query(default=None, description="Filter persons of registered users"),
        filter_model: PersonFilter = FilterDepends(PersonFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: PersonsService = PersonsService(
        session=session
    )
    result_full = await service.get_all_full(
        filter_model=filter_model,
        db_persons=for_registered_users,
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
    response_model=PersonShort,
    description="Get personal item"
)
@RateLimiter.rate_limit()
async def get_one_of_me(
        request: Request,
        person: Union["Person", "SessionPerson"] = Depends(deps.get_person_session),
):
    return await utils.get_short_schema_from_orm(person)


# 5_2
@router.get(
    "/{user_id}",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_200_OK,
    response_model=PersonShort,
    description="Get item by user_id"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: PersonsService = PersonsService(
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
    response_model=PersonRead,
    description="Get personal item full"
)
@RateLimiter.rate_limit()
async def get_one_full_of_me_session(
        request: Request,
        person: Union["Person", "SessionPerson"] = Depends(deps.get_person_session_full),
):
    return await utils.get_schema_from_orm(person)


# 6_2
@router.get(
    "/{user_id}/full",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=PersonRead,
    description="Get full item by user_id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_full(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: PersonsService = PersonsService(
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
    response_model=PersonRead,
    description="Create one personal item"
)
@RateLimiter.rate_limit()
async def create_one(
        request: Request,
        firstname: str = Form(min_length=2, max_length=50),
        lastname: Optional[str] = Form(max_length=50, default=None),
        company_name: Optional[str] = Form(min_length=2, max_length=100, default=None),
        user: "User" = Depends(current_user_or_none),
        session_data: "SessionData" = Depends(verifier_or_none),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):

    service: PersonsService = PersonsService(
        session=session,
        session_data=session_data
    )
    return await service.create_one(
        user=user,
        firstname=firstname,
        lastname=lastname,
        company_name=company_name
    )







#
#

#
#
# # 7
# @router.post(
#     "",
#     dependencies=[Depends(current_user),],
#     status_code=status.HTTP_201_CREATED,
#     response_model=PostRead,
#     description="Create one item"
# )
# @RateLimiter.rate_limit()
# async def create_one(
#         request: Request,
#         product_id: Optional[int] = Form(default=None, gt=0),
#         name: str = Form(),
#         review: str = Form(),
#         user: "User" = Depends(current_user),
#         session: AsyncSession = Depends(DBConfigurer.session_getter)
# ):
#
#     service: PostsService = PostsService(
#         session=session
#     )
#     return await service.create_one(
#         user=user,
#         product_id=product_id,
#         name=name,
#         review=review,
#     )
#
#
# # 8
# @router.delete(
#     "/{id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     description="Delete item by id (for superuser and item's author only)"
# )
# @RateLimiter.rate_limit()
# async def delete_one(
#         request: Request,
#         user: "User" = Depends(current_user),
#         orm_model: "Vote" = Depends(deps.get_one_simple),
#         session: AsyncSession = Depends(DBConfigurer.session_getter),
# ):
#     service: PostsService = PostsService(
#         session=session
#     )
#     return await service.delete_one(
#         orm_model=orm_model,
#         user=user
#     )
#
#
# # 9
# @router.put(
#         "/{id}",
#         status_code=status.HTTP_200_OK,
#         response_model=PostRead,
#         description="Edit item by id (for superuser and item's author only)"
# )
# @RateLimiter.rate_limit()
# async def put_one(
#         request: Request,
#         user: "User" = Depends(current_user),
#         orm_model: "Post" = Depends(deps.get_one_simple),
#         product_id: Optional[int] = Form(default=None, gt=0),
#         name: str = Form(),
#         review: str = Form(),
#         session: AsyncSession = Depends(DBConfigurer.session_getter),
# ):
#     service: PostsService = PostsService(
#         session=session
#     )
#     return await service.edit_one(
#         orm_model=orm_model,
#         user=user,
#         product_id=product_id,
#         name=name,
#         review=review,
#     )
#
#
# # 10
# @router.patch(
#         "/{id}",
#         status_code=status.HTTP_200_OK,
#         response_model=PostRead,
#         description="Partial edit item by id (for superuser and item's author only)"
# )
# @RateLimiter.rate_limit()
# async def patch_one(
#         request: Request,
#         user: "User" = Depends(current_user),
#         orm_model: "Post" = Depends(deps.get_one_simple),
#         product_id: Optional[int] = Form(default=None),
#         reset_product: Optional[bool] = Form(default=None),
#         name: Optional[str] = Form(default=None),
#         review: Optional[str] = Form(default=None),
#         session: AsyncSession = Depends(DBConfigurer.session_getter),
# ):
#     service: PostsService = PostsService(
#         session=session
#     )
#     return await service.edit_one(
#         orm_model=orm_model,
#         user=user,
#         product_id=product_id,
#         name=name,
#         review=review,
#         reset_product=reset_product,
#         is_partial=True
#     )
#
#
# # 11_1
# @router.get(
#     "/{id}/user",
#     dependencies=[Depends(current_superuser), ],
#     status_code=status.HTTP_200_OK,
#     response_model=UserPublicExtended,
#     description="Get item relations user by id (for superuser only)"
# )
# # @RateLimiter.rate_limit()
# # no rate limit for superuser
# async def get_relations_user(
#         request: Request,
#         id: int,
#         session: AsyncSession = Depends(DBConfigurer.session_getter)
# ):
#     service: PostsService = PostsService(
#         session=session
#     )
#     return await service.get_one_complex(
#         id=id,
#         maximized=False,
#         relations=['user',]
#     )
#
#
# # 11_2
# @router.get(
#     "/{id}/product",
#     status_code=status.HTTP_200_OK,
#     description="Get item relations product by id"
# )
# @RateLimiter.rate_limit()
# async def get_relations_product(
#         request: Request,
#         id: int,
#         session: AsyncSession = Depends(DBConfigurer.session_getter)
# ) -> ProductShort | None:
#     service: PostsService = PostsService(
#         session=session
#     )
#     return await service.get_one_complex(
#         id=id,
#         maximized=False,
#         relations=['product',]
#     )
