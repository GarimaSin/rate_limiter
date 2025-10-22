\
        \"\"\"Redis-backed token bucket using Lua for atomic operations.

        The Lua script is stored in `TOKEN_BUCKET_LUA`. It accepts keys:
          KEYS[1] = token key in Redis
        And ARGV:
          ARGV[1] = capacity
          ARGV[2] = refill_rate (tokens per second)
          ARGV[3] = now (current timestamp in seconds as float string)
          ARGV[4] = tokens_to_consume (int)

        Returns 1 if tokens consumed (allowed), 0 if not allowed, and also sets TTL on key.
        \"\"\"
        import time
        import math

        TOKEN_BUCKET_LUA = r\"\"\"\
        -- ARGV[1] capacity
        -- ARGV[2] refill_rate
        -- ARGV[3] now (float seconds)
        -- ARGV[4] tokens_to_consume
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local tokens_req = tonumber(ARGV[4])

        local data = redis.call('HMGET', KEYS[1], 'tokens', 'last')
        local tokens = tonumber(data[1])
        local last = tonumber(data[2])
        if tokens == nil then
            tokens = capacity
            last = now
        end

        -- refill
        local elapsed = now - last
        if elapsed > 0 then
            local added = elapsed * refill_rate
            tokens = math.min(capacity, tokens + added)
            last = now
        end

        if tokens_req <= tokens then
            tokens = tokens - tokens_req
            redis.call('HMSET', KEYS[1], 'tokens', tostring(tokens), 'last', tostring(last))
            -- set TTL to something like 2x capacity/refill (heuristic) to cleanup idle keys
            local ttl = math.ceil((capacity / refill_rate) * 2)
            redis.call('EXPIRE', KEYS[1], ttl)
            return 1
        else
            -- update the tokens/last so future calls see the new last timestamp
            redis.call('HMSET', KEYS[1], 'tokens', tostring(tokens), 'last', tostring(last))
            redis.call('EXPIRE', KEYS[1],  math.ceil((capacity / refill_rate) * 2))
            return 0
        end
        \"\"\"

        class RedisTokenBucket:
            def __init__(self, redis_client, capacity: int, refill_rate: float, prefix: str = 'rl:'):
                \"\"\"redis_client should follow redis-py interface (redis.Redis)\n                `capacity` integer, `refill_rate` tokens/second\n                \"\"\"
                self.redis = redis_client
                self.capacity = int(capacity)
                self.refill_rate = float(refill_rate)
                self.prefix = prefix
                # script can be registered; many redis clients allow script loading, but we'll use EVAL for simplicity
                self._lua = TOKEN_BUCKET_LUA

            def _key(self, key: str) -> str:
                return f\"{self.prefix}{key}\"

            def consume(self, key: str, tokens: int = 1) -> bool:
                now = time.time()
                res = self.redis.eval(self._lua, 1, self._key(key), self.capacity, self.refill_rate, now, tokens)
                # redis-py returns int reply
                return int(res) == 1

            def get_state(self, key: str):
                h = self.redis.hgetall(self._key(key))
                if not h:
                    return {'tokens': self.capacity, 'last': time.time()}
                # convert bytes to str/float depending on client
                tokens = float(h.get(b'tokens') if isinstance(h.get(b'tokens'), bytes) else h.get('tokens'))
                last = float(h.get(b'last') if isinstance(h.get(b'last'), bytes) else h.get('last'))
                return {'tokens': tokens, 'last': last}
