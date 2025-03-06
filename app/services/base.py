import json
from typing import Any, Dict, Optional

from bson import json_util

from app.db.redis_client import redis_client


class BaseService:
    """Base class for all services"""

    @staticmethod
    def serialize_mongodb_doc(doc: Dict) -> Dict:
        """Convert MongoDB document to JSON serializable format"""
        return json.loads(json_util.dumps(doc))

    @staticmethod
    async def get_cached_data(key: str) -> Optional[Dict]:
        """
        Retrieve data from cache using the provided key.

        Args:
            key (str): The cache key to retrieve data for

        Returns:
            Optional[Dict]: The cached data if it exists, None otherwise
        """
        return await redis_client.get_cached_data(key)

    @staticmethod
    async def set_cached_data(key: str, data: Any) -> None:
        """
        Store data in cache with the provided key.

        Args:
            key (str): The cache key to store the data under
            data (Any): The data to be cached

        Returns:
            None
        """
        if data:
            await redis_client.set_cached_data(key, data)
