import hashlib
import time
from functools import wraps
from typing import Callable, Any
from fastapi import Request, status
from fastapi.responses import ORJSONResponse


class RateLimiter:

    @staticmethod
    def rate_limit(
            max_calls: int = 60,
            period: int = 60,
    ):
        def decorator(
                func: Callable[[Request, Any], Any]
        ) -> Callable[[Request, Any], Any]:

            usage: dict[str, list[float]] = {}

            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs) -> Any:
                if not request.client:
                    return ORJSONResponse(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        content={
                            "message": "Handled by Rate Limiter exception handler",
                            "detail": "Request has no client information",
                        }
                    )

                ip_address: str = request.client.host
                unique_id: str = hashlib.sha256(ip_address.encode()).hexdigest()
                now = time.time()

                if unique_id not in usage:
                    usage[unique_id] = []

                timestamps = usage[unique_id]
                timestamps[:] = [t for t in timestamps if now - t < period]

                if len(timestamps) < max_calls:
                    timestamps.append(now)
                    return await func(request, *args, **kwargs)

                wait: float = period - (now - timestamps[0])
                return ORJSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "message": "Handled by Rate Limiter exception handler",
                        "detail": f"Rate limit exceed. Retry after {wait:.2f} seconds",
                    }
                )

            return wrapper

        return decorator
