# main.py
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import json, math, asyncio, os
from .rate_limiter import RateLimiter

with open("lua/token_bucket.lua") as f: LUA_SCRIPT=f.read()

limiter=RateLimiter(redis_url=os.getenv("REDIS_URL","redis://localhost:6379/0"),lua_script=LUA_SCRIPT)
asyncio.get_event_loop().run_until_complete(limiter.init())

class RLMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,req,call_next):
        key=f"rl:{req.client.host}:{req.url.path.replace('/','_')}"
        ok,left,retry=await limiter.allow(key,100,200)
        if not ok:
            hdr={"Retry-After":str(math.ceil(retry/1000))}
            return Response(json.dumps({"detail":"Too Many Requests"}),status_code=HTTP_429_TOO_MANY_REQUESTS,headers=hdr)
        resp=await call_next(req)
        resp.headers["X-RateLimit-Remaining"]=str(left or 0)
        return resp

app=FastAPI()
app.add_middleware(RLMiddleware)

@app.get("/ping")
async def ping(): return {"ok":True}
