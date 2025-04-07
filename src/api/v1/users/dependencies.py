from src.api.v1.auth.backend import fastapi_users


current_user = fastapi_users.current_user(
    active=True,
    verified=True,
)

current_superuser = fastapi_users.current_user(
    active=True,
    verified=True,
    superuser=True,
)

current_user_or_none = fastapi_users.current_user(
    optional=True,
    active=True,
    verified=True,
)