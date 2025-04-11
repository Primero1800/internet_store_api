from typing import Any

from fastapi import APIRouter, Request, Response, status, Depends

from src.api.v1.users.dependencies import current_user_or_none
from src.core.config import RateLimiter

from .service import SessionsService


router = APIRouter()


@router.post(
    "/create_session"
)
@RateLimiter.rate_limit()
async def create_session(
        request: Request,
        response: Response,
        user: Any = Depends(current_user_or_none),
):
    service: SessionsService = SessionsService()
    return await service.create_session(

    )