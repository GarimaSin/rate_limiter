"""FastAPI middleware for rate limiting using a provided backend.

The middleware extracts a key from the request (by default client IP) and checks
with the configured backend whether the request should be allowed.
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, backend, capacity: int = 10, refill_rate: float = 1.0, key_extractor=None):
        super().__init__(app)
        self.backend = backend
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.key_extractor = key_extractor or (lambda request: request.client.host if request.client else 'anonymous')

    async def dispatch(self, request: Request, call_next):
        key = self.key_extractor(request)
        allowed = self.backend.consume(key, tokens=1)
        if not allowed:
            return Response('Too Many Requests', status_code=429)
        # proceed
        response = await call_next(request)
        return response
