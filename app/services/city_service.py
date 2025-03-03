from typing import Dict, List

from app.db.bigquery import bigquery_client
from app.services.base import BaseService


class CityService(BaseService):
    @staticmethod
    async def get_cities() -> List[Dict[str, str]]:
        """
        Retrieve a list of all available cities.

        Returns:
            List[Dict[str, str]]: List of city names

        Note:
            Results are cached to improve performance
        """
        cache_key = "cities_list"
        cached_data = await CityService.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        cities = await bigquery_client.get_cities()
        await CityService.set_cached_data(cache_key, cities)
        return cities

    @staticmethod
    async def get_city_metrics(city_name: str) -> Dict:
        """
        Get detailed metrics for a specific city.

        Args:
            city_name (str): Name of the city to get metrics for

        Returns:
            Dict: City metrics including revenue, retailer count, and neighborhood data

        Note:
            Results are cached to improve performance
        """
        cache_key = f"city_metrics_{city_name}"
        cached_data = await CityService.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        metrics = await bigquery_client.get_city_metrics(city_name)
        await CityService.set_cached_data(cache_key, metrics)
        return metrics


city_service = CityService()
