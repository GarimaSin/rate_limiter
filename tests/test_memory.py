import time
from rate_limiter.algorithms import TokenBucketMemory

def test_memory_consume_and_refill():
    b = TokenBucketMemory(capacity=3, refill_rate=1.0)
    assert b.consume(1)
    assert b.consume(1)
    assert b.consume(1)
    # now empty
    assert not b.consume(1)
    # wait to refill one token
    time.sleep(1.05)
    assert b.consume(1)
