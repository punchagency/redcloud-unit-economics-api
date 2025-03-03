from typing import Dict

from db.bigquery import bigquery_client
from services.base import BaseService


class NeighborhoodService(BaseService):
    @staticmethod
    async def get_neighborhood_metrics(city_name: str, neighborhood_name: str) -> Dict:
        """
        Get detailed metrics for a specific neighborhood within a city.

        Args:
            city_name (str): Name of the city
            neighborhood_name (str): Name of the neighborhood

        Returns:
            Dict: Neighborhood metrics including retailer density, revenue,
                and individual retailer data

        Note:
            Results are cached to improve performance
        """
        cache_key = f"neighborhood_metrics_{city_name}_{neighborhood_name}"
        cached_data = await NeighborhoodService.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        metrics = await bigquery_client.get_neighborhood_metrics(
            city_name, neighborhood_name
        )
        await NeighborhoodService.set_cached_data(cache_key, metrics)
        return metrics


neighborhood_service = NeighborhoodService()
