from app.cache import CacheClient


class RateLimiter:

    def __init__(self, cache_client: CacheClient, limit: int, window_seconds: int):
        self.cache_client = cache_client
        self.limit = limit
        self.window_seconds = window_seconds

    def check(self, key: str) -> bool:
        count = self.cache_client.record_and_count(key, self.window_seconds)
        return count <= self.limit
