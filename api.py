"""FastAPI demo that uses both in-memory and Redis backends.
Use REDIS_URL env var to enable Redis backend.
"""
import os
from fastapi import FastAPI, Depends, HTTPException
from rate_limiter.algorithms import TokenBucketMemory
from rate_limiter.backends import RedisTokenBucket
from rate_limiter.middleware import RateLimitMiddleware
from pydantic import BaseModel
import redis

app = FastAPI(title='Rate Limiter Demo')

# default in-memory limiter per IP (capacity 10, refill 1 token/sec)
mem_backend = TokenBucketMemory(capacity=10, refill_rate=1.0)

# Redis backend (distributed) -- requires REDIS_URL or will not be used
REDIS_URL = os.environ.get('REDIS_URL', None)
redis_backend = None
if REDIS_URL:
    r = redis.Redis.from_url(REDIS_URL)
    # note: for production tuning, use connection pooling and async client if needed
    redis_backend = RedisTokenBucket(r, capacity=20, refill_rate=2.0)

# choose active backend: prefer redis if available
active_backend = redis_backend or mem_backend

# add middleware that applies rate limiting globally
app.add_middleware(RateLimitMiddleware, backend=active_backend, capacity=20, refill_rate=2.0)

class Info(BaseModel):
    key: str

@app.get('/status')
def status():
    return {'backend': 'redis' if redis_backend else 'memory'}

@app.post('/consume')
def consume(info: Info):
    allowed = active_backend.consume(info.key, tokens=1)
    return {'allowed': bool(allowed)}

@app.get('/state/{key}')
def state(key: str):
    if hasattr(active_backend, 'get_state'):
        return active_backend.get_state(key)
    raise HTTPException(status_code=404, detail='State not available for this backend')
