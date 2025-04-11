from typing import Any

from fastapi import APIRouter, Request, Response, status, Depends

from src.api.v1.users.dependencies import current_user_or_none
from src.core.config import RateLimiter
from src.core.sessions.fastapi_sessions_config import SessionData

from .service import SessionsService


router = APIRouter()


@router.post(
    "/create_session",
    response_model=SessionData,
    status_code=status.HTTP_201_CREATED,
)
@RateLimiter.rate_limit()
async def create_session(
        request: Request,
        response: Response,
        user: Any = Depends(current_user_or_none),
):
    service: SessionsService = SessionsService()
    return await service.create_session(
        user=user,
        response=response,
    )