# Scalable Rate Limiter (Python)

This project implements a flexible, production-minded rate limiter with:
- In-memory token bucket (single-process)
- Redis-backed token bucket (distributed)
- FastAPI demo with middleware to protect endpoints
- CLI utilities and pytest unit tests

Features
- Configurable capacity and refill rate (tokens/second)
- Redis implementation uses Lua script for atomic token consumption
- Middleware integrates with FastAPI to rate-limit requests per key (IP or API key)

Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run HTTP demo (requires Redis for full distributed behavior)
uvicorn api:app --reload

# Run tests (uses a FakeRedis implementation for unit tests)
pytest -q
```

Notes
- For distributed usage, run a Redis instance and configure `REDIS_URL` in environment.
- The Redis Lua script ensures atomic check-and-decrement for token buckets.
