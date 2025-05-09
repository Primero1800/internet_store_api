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

from src.core.sessions.fastapi_sessions_config import cookie_or_none, SessionData, verifier_or_none
from src.scrypts.pagination import paginate_result
from src.tools.customer_payment_choices import CustomerPaymentChoices
from src.tools.moveto_choices import MoveToChoices
from .service import OrdersService
from .schemas import (
    OrderRead,
    OrderShort,
)
from .filters import OrderFilter
from src.api.v1.users.user.dependencies import (
    current_superuser,
    current_user, current_user_or_none,
)
from src.core.config import DBConfigurer, RateLimiter
from . import dependencies as deps
from ..person import dependencies as person_deps
from ..address import dependencies as address_deps
from ...carts import dependencies as carts_deps
from . import utils

if TYPE_CHECKING:
    from src.core.models import (
        User,
        Order,
        Address,
        Cart,
        Person,
    )
    from src.api.v1.carts.session_cart import SessionCart
    from src.api.v1.orders.person.session_person import SessionPerson
    from src.api.v1.orders.address.session_address import SessionAddress



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


3
@router.get(
    "",
    dependencies=[Depends(current_superuser),],
    response_model=List[OrderShort],
    status_code=status.HTTP_200_OK,
    description="Get items list (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: OrderFilter = FilterDepends(OrderFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: OrdersService = OrdersService(
        session=session
    )
    result_full = await service.get_all(
        filter_model=filter_model
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
    response_model=List[OrderRead],
    status_code=status.HTTP_200_OK,
    description="Get full items list (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: OrderFilter = FilterDepends(OrderFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: OrdersService = OrdersService(
        session=session
    )
    result_full = await service.get_all_full(filter_model=filter_model)
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 7
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(cookie_or_none),],
    response_model=OrderRead,
    description="Create one item"
)
@RateLimiter.rate_limit()
async def create_one(
        request: Request,

        move_to: MoveToChoices = Form(
            default=MoveToChoices.TO_CUSTOMER_ADDRESS,
            description="Order's delivery ways"
        ),
        payment_ways: CustomerPaymentChoices = Form(
            default=CustomerPaymentChoices.P_IN_ADVANCE,
            description="Order's payment ways"
        ),

        user: "User" = Depends(current_user_or_none),
        cart: Union["Cart", "SessionCart"] = Depends(carts_deps.get_or_create_cart_session),
        person: Union["Person", "SessionPerson"] = Depends(person_deps.get_one_session),
        address:  Union["Address", "SessionAddress"] = Depends(address_deps.get_one_session),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        session_data: SessionData = Depends(verifier_or_none),
):

    service: OrdersService = OrdersService(
        session=session,
        session_data=session_data
    )
    return await service.create_one(
        user=user,
        cart=cart,
        person=person,
        address=address,
        move_to=move_to,
        payment_ways=payment_ways,
        to_schema=True,
    )
