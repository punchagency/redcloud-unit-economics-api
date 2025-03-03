from typing import Dict, List

from app.db.bigquery import bigquery_client
from app.services.base import BaseService


class RetailerService(BaseService):
    @staticmethod
    async def get_retailer_metrics(seller_id: int) -> Dict:
        """
        Get detailed metrics for a specific retailer.

        Args:
            seller_id (int): The unique identifier of the seller/retailer

        Returns:
            Dict: Retailer metrics including revenue, orders, and location data

        Note:
            Results are cached to improve performance
        """
        cache_key = f"retailer_metrics_{seller_id}"
        cached_data = await RetailerService.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        metrics = await bigquery_client.get_retailer_metrics(seller_id)
        await RetailerService.set_cached_data(cache_key, metrics)
        return metrics

    @staticmethod
    async def search_retailers(query: str, city: str = None) -> List[Dict]:
        """
        Search for retailers by name with optional city filter.

        Args:
            query (str): Search query string
            city (str, optional): City name to filter results. Defaults to None.

        Returns:
            List[Dict]: List of matching retailers with their metrics

        Note:
            Results are cached to improve performance
            Search is case-insensitive and uses partial matching
        """
        cache_key = f"retailer_search_{city}_{query}"
        cached_data = await RetailerService.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        results = await bigquery_client.search_retailers(query, city)
        await RetailerService.set_cached_data(cache_key, results)
        return results


retailer_service = RetailerService()
