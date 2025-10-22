"""CLI to test the rate limiters locally."""
import argparse
from rate_limiter.algorithms import TokenBucketMemory
from rate_limiter.backends import RedisTokenBucket
import redis, os, time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--redis', action='store_true', help='Use redis backend (requires REDIS_URL env var)')
    parser.add_argument('--key', default='test-user', help='Key to consume tokens for')
    parser.add_argument('--count', type=int, default=5)
    args = parser.parse_args()

    if args.redis:
        REDIS_URL = os.environ.get('REDIS_URL')
        if not REDIS_URL:
            print('Set REDIS_URL env var to use redis backend')
            return
        r = redis.Redis.from_url(REDIS_URL)
        backend = RedisTokenBucket(r, capacity=10, refill_rate=1.0)
    else:
        backend = TokenBucketMemory(capacity=5, refill_rate=0.5)

    for i in range(args.count):
        ok = backend.consume(args.key, tokens=1)
        print(f'Attempt {i+1}:', 'allowed' if ok else 'rate-limited')
        time.sleep(0.5)

if __name__ == '__main__':
    main()
