import time
import uuid
from redis import Redis


class CacheClient:

    def __init__(self, client: Redis):
        self.client = client

    def record_and_count(self, key: str, window_seconds: int) -> int:
        now = time.time()
        cutoff = now - window_seconds
        pipe = self.client.pipeline()
        pipe.zremrangebyscore(key, 0, cutoff)
        pipe.zadd(key, {str(uuid.uuid4()): now})
        pipe.zcard(key)
        pipe.expire(key, window_seconds)
        return pipe.execute()[2]
