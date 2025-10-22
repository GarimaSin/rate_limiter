\
        import time
        from rate_limiter.backends import RedisTokenBucket
        # FakeRedis is a minimal in-memory stand-in for redis.Redis for testing
        class FakeRedis:
            def __init__(self):
                self.store = {}
            def eval(self, script, numkeys, key, capacity, refill_rate, now, tokens_req):
                # naive python implementation of lua logic for testing only (not production accurate)
                k = key
                entry = self.store.get(k, {'tokens': float(capacity), 'last': float(now)})
                tokens = float(entry['tokens'])
                last = float(entry['last'])
                elapsed = float(now) - last
                if elapsed > 0:
                    tokens = min(float(capacity), tokens + elapsed * float(refill_rate))
                    last = float(now)
                if int(tokens_req) <= tokens:
                    tokens = tokens - int(tokens_req)
                    self.store[k] = {'tokens': tokens, 'last': last}
                    return 1
                else:
                    self.store[k] = {'tokens': tokens, 'last': last}
                    return 0

        def test_redis_token_bucket_fake():
            fake = FakeRedis()
            rb = RedisTokenBucket(fake, capacity=2, refill_rate=1.0)
            assert rb.consume('u1', tokens=1)
            assert rb.consume('u1', tokens=1)
            assert not rb.consume('u1', tokens=1)
            time.sleep(1.05)
            assert rb.consume('u1', tokens=1)
