from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Request, Response, status, Depends, Body, Query

from src.api.v1.users.dependencies import (
    current_user_or_none,
    current_user,
    current_superuser,
)
from src.core.config import RateLimiter
from src.core.sessions.fastapi_sessions_config import (
    SessionData,
    cookie,
    verifier,
)
from src.scrypts.pagination import paginate_result
from .service import SessionsService


router = APIRouter()


@router.post(
    "/create_session",
    response_model=SessionData,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
)
@RateLimiter.rate_limit()
async def create_session(
        request: Request,
        response: Response,
        data: dict | None = Body(...),
        user: Any = Depends(current_user_or_none),
):
    service: SessionsService = SessionsService()
    return await service.create_session(
        user=user,
        response=response,
        session_data=data,
    )


@router.post(
    "/set_session",
    response_model=SessionData,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
@RateLimiter.rate_limit()
async def set_current_session(
        request: Request,
        response: Response,
        user: Any = Depends(current_user)
):
    service: SessionsService = SessionsService()
    return await service.set_current_session(
        user=user,
        response=response,
    )


@router.get(
    "/whoami",
    dependencies=[Depends(cookie)],
    response_model=SessionData,
    response_model_exclude_unset=True,
)
@RateLimiter.rate_limit()
async def whoami(
    request: Request,
    session_data: SessionData = Depends(verifier),
):
    service: SessionsService = SessionsService()
    return await service.get_current_session(
        session_data=session_data,
    )


@router.post(
    "/delete_session",
    status_code=status.HTTP_204_NO_CONTENT
)
@RateLimiter.rate_limit()
async def del_session(
        request: Request,
        response: Response,
        session_id: UUID = Depends(cookie)
):
    service: SessionsService = SessionsService()
    return await service.delete_session(
        session_id=session_id,
        response=response,
    )


@router.post(
    "/update_session",
    dependencies=[Depends(cookie)],
    response_model=SessionData,
)
@RateLimiter.rate_limit()
async def update_session(
        request: Request,
        data: Dict[str, Any],
        session_id: UUID = Depends(cookie),
        session_data: SessionData = Depends(verifier)
):
    service: SessionsService = SessionsService()

    return await service.update_session(
        data_to_update=data,
        session_data=session_data,
        session_id=session_id,
    )


@router.post(
    "/clear_session",
    status_code=status.HTTP_200_OK,
    response_model=SessionData,
)
@RateLimiter.rate_limit()
async def clear_session(
        request: Request,
        session_id: UUID = Depends(cookie),
        session_data: SessionData = Depends(verifier)
):
    service: SessionsService = SessionsService()
    return await service.clear_session(
        session_id=session_id,
        session_data=session_data,
    )


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    response_model=list[SessionData],
    dependencies=[Depends(current_superuser),]
)
@RateLimiter.rate_limit()
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
):
    service: SessionsService = SessionsService()
    result_full = await service.get_all()
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )
