from fastapi_users import FastAPIUsers
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from sqlalchemy import Integer

from src.api.v1.auth.dependencies import get_user_manager
from src.core.settings import settings


bearer_transport = BearerTransport(
    tokenUrl=settings.auth.get_url(purpose="transport-token", version="v1")
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.auth.AUTH_PRIVATE_KEY.read_text(),
        lifetime_seconds=settings.auth.AUTH_TOKEN_LIFETIME,
        algorithm="RS256",
        public_key=settings.auth.AUTH_PUBLIC_KEY.read_text(),
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users

fastapi_users = FastAPIUsers["User", Integer](
    get_user_manager,
    [auth_backend],
)
