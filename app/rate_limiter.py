# rate_limiter.py
# (Simplified snippet, full version in explanation)
import time, math, asyncio, redis.asyncio as aioredis
from dataclasses import dataclass

@dataclass
class LocalBucket:
    capacity: float
    tokens: float
    rate_per_sec: float
    last_ts: float
    def consume(self, amount: float=1.0):
        now=time.time();elapsed=now-self.last_ts
        if elapsed>0:self.tokens=min(self.capacity,self.tokens+elapsed*self.rate_per_sec);self.last_ts=now
        if self.tokens>=amount:self.tokens-=amount;return True,self.tokens
        else:return False,(amount-self.tokens)/self.rate_per_sec

class RateLimiter:
    def __init__(self, redis_url, lua_script, key_ttl_ms=60000, permissive_on_redis_down=True):
        self.redis=aioredis.from_url(redis_url,decode_responses=True)
        self.lua=lua_script;self.sha=None;self.key_ttl_ms=key_ttl_ms
        self.local_buckets={};self.lock=asyncio.Lock()
        self.permissive_on_redis_down=permissive_on_redis_down
    async def init(self):
        self.sha=await self.redis.script_load(self.lua)
    async def allow(self,key,rate,burst):
        now_ms=int(time.time()*1000)
        async with self.lock:
            b=self.local_buckets.get(key) or LocalBucket(burst,burst,rate,time.time());self.local_buckets[key]=b
            ok,info=b.consume(1); 
            if ok:return True,int(info),0
        try:
            res=await self.redis.evalsha(self.sha,1,key,now_ms,rate,burst,1,self.key_ttl_ms)
            return bool(int(res[0])),int(res[1]),int(res[2])
        except: return True,None,0
