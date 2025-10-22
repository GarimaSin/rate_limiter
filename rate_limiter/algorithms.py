"""In-memory token bucket implementation (thread-safe)."""
import threading
import time

class TokenBucketMemory:
    def __init__(self, capacity: int, refill_rate: float):
        """Create a memory token bucket.

        :param capacity: maximum tokens in the bucket
        :param refill_rate: tokens added per second
        """
        self.capacity = int(capacity)
        self.refill_rate = float(refill_rate)
        self._tokens = float(capacity)
        self._last = time.time()
        self._lock = threading.Lock()

    def _refill(self):
        now = time.time()
        elapsed = now - self._last
        if elapsed <= 0:
            return
        added = elapsed * self.refill_rate
        self._tokens = min(self.capacity, self._tokens + added)
        self._last = now

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Return True if allowed."""
        with self._lock:
            self._refill()
            if tokens <= self._tokens:
                self._tokens -= tokens
                return True
            return False

    def get_tokens(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens
