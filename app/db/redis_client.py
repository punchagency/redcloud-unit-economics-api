import json

import redis
from app.core.config import settings


class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

    async def get_cached_data(self, key: str):
        """
        Get cached data from Redis.

        Args:
            key (str): The key to retrieve data from
        Returns:
            Optional[Dict]: The cached data if it exists, None otherwise
        """
        data = self.redis.get(key)
        return json.loads(data) if data else None

    async def set_cached_data(self, key: str, data: dict):
        """
        Set cached data in Redis.

        Args:
            key (str): The key to store the data under
            data (dict): The data to store

        Returns:
            None
        """
        self.redis.setex(key, settings.REDIS_TTL, json.dumps(data))


redis_client = RedisClient()
