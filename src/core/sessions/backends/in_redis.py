import json
from typing import Dict, Generic

import redis
from fastapi_sessions.backends.session_backend import (
    BackendError,
    SessionBackend,
    SessionModel,
)
from fastapi_sessions.frontends.session_frontend import ID

from src.core.settings import settings


class InRedisBackend(Generic[ID, SessionModel], SessionBackend[ID, SessionModel]):
    """Stores session data on redis-server."""

    def __init__(self) -> None:
        """Initialize a new in-memory database."""

        # self.data: Dict[ID, SessionModel] = {}
        self.service: redis.asyncio.Redis = redis.asyncio.Redis(
            host=settings.redis.REDIS_HOST,
            port=settings.redis.REDIS_PORT,
            db=settings.redis.REDIS_DATABASE,
        )
        self.expired = settings.redis.REDIS_CACHE_LIFETIME_SECONDS
        self.prefix = f"{settings.app.APP_NAME}_session:"

    def get_redis_key(self, session_id: ID):
        return f"{self.prefix}{session_id}"

    async def create(self, session_id: ID, data: SessionModel):
        """Create a new session entry."""
        async with self.service as client:
            redis_key = self.get_redis_key(session_id)
            redis_data = await client.get(redis_key)
            if redis_data:
                raise BackendError("Session already exists, Can't overwrite existing session.")

            await client.set(
                redis_key,
                json.dumps(data),
                ex=self.expired
            )

    async def read(self, session_id: ID):
        """Read an existing session data."""
        async with self.service as client:
            redis_key =  self.get_redis_key(session_id)
            redis_data = await client.get(redis_key)
            if not redis_data:
                return
            return json.loads(redis_data)

    async def update(self, session_id: ID, data: SessionModel) -> None:
        """Update an existing session."""
        async with self.service as client:
            redis_key = self.get_redis_key(session_id)
            redis_data = await client.get(redis_key)
            if not redis_data:
                raise BackendError("Session does not exist, cannot update")
            redis_data_decoded: dict = json.loads(redis_data)
            redis_data_decoded.update(data)

            await client.set(
                redis_key,
                json.dumps(redis_data_decoded),
                ex=self.expired
            )

    async def delete(self, session_id: ID) -> None:
        """Delete session from redis-server"""
        async with self.service as client:
            redis_key = self.get_redis_key(session_id)
            await client.delete(redis_key)
