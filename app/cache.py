import os

import redis


class RedisCache:
    def __init__(self):
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", 6379)
        self.client = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.ttl = 3600

    def set(self, key, value):
        self.client.setex(key, self.ttl, value)

    def get(self, key):
        return self.client.get(key)
