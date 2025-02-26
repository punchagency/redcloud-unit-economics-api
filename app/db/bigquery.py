from functools import lru_cache
from typing import Dict, List, Optional

from core.config import settings
from google.api_core import exceptions, retry
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
from rich.console import Console

console = Console()


class BigQueryClient:
    """
    Client for interacting with Google BigQuery.
    Provides optimized query execution and caching for common queries.
    """

    def __init__(self):
        """Initialize BigQuery client with project and dataset configuration."""
        self.client = bigquery.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        self.dataset = settings.BIGQUERY_DATASET
        # Prepare commonly used tables
        self._orders_table = f"`{self.dataset}.marketplace_order_copy`"
        self._neighborhoods_table = f"`{self.dataset}.marketplace_order_copy`"

    @retry.Retry(
        predicate=retry.if_exception_type(
            exceptions.ServerError,
            exceptions.BadRequest,
            exceptions.BadGateway,
        ),
        initial=1.0,  # Initial delay in seconds
        maximum=60.0,  # Maximum delay in seconds
        multiplier=2.0,  # Delay multiplier
        deadline=600.0  # Maximum total time to retry in seconds
    )
    async def execute_query(
        self,
        query: str,
        params: Optional[List[ScalarQueryParameter]] = None,
        timeout: int = 30,
    ) -> List[Dict]:
        """
        Execute a BigQuery query with retry logic and timeout.

        Args:
            query (str): SQL query string
            params (Optional[List[ScalarQueryParameter]]): Query parameters
            timeout (int): Query timeout in seconds. Defaults to 30.

        Returns:
            List[Dict]: Query results as list of dictionaries

        Raises:
            Exception: If query execution fails
        """
        try:
            job_config = QueryJobConfig(query_parameters=params) if params else None
            query_job = self.client.query(query, job_config=job_config, timeout=timeout)
            return [dict(row) for row in query_job]
        except Exception as e:
            console.log(f"[red]Error executing query: {e}[/red]")
            raise

    @lru_cache(maxsize=100)
    def get_base_retailer_query(self) -> str:
        """
        Get cached base query for retailer metrics.

        Returns:
            str: Base SQL query for retailer metrics

        Note:
            Result is cached using lru_cache
        """
        return f"""
        SELECT 
            Seller_ID as seller_id,
            Seller_Name as seller_name,
            Store_Name as store_name,
            Internal_Seller_Latitude as internal_seller_latitude,
            Internal_Seller_Longitude as internal_seller_longitude,
            SUM(Gross_TTV_USD) as gross_ttv_usd,
            SUM(Revenue_USD) as revenue_usd,
            COUNT(DISTINCT Order_ID) as total_orders,
            ARRAY_AGG(DISTINCT Product_Category) as product_categories
        FROM {self._orders_table}
        """

    async def get_cities(self) -> List[Dict[str, str]]:
        """
        Get a list of all unique cities from the orders table.

        Returns:
            List[Dict[str, str]]: List of cities with their names
        """
        query = f"""
        SELECT DISTINCT 
            Shipping_City as city
        FROM {self._orders_table}
        WHERE 
            Shipping_City IS NOT NULL
            AND Shipping_City != ''
        ORDER BY city ASC
        """
        return await self.execute_query(query)

    async def get_city_metrics(self, city_name: str) -> Dict:
        """
        Get city-level metrics including total revenue, retailer count, and average TTV.

        Args:
            city_name (str): Name of the city to get metrics for

        Returns:
            Dict: City metrics including revenue, retailer count, and average TTV

        Note:
            Results are cached to improve performance
        """
    

        query = f"""
        WITH retailer_metrics AS (
            SELECT 
                Shipping_City as city,
                SUM(Revenue_USD) as total_revenue_usd,
                COUNT(DISTINCT Seller_ID) as total_retailers,
                AVG(Gross_TTV_USD) as avg_ttv_usd
            FROM {self._orders_table}
            WHERE Shipping_City = @city
            GROUP BY Shipping_City
        )
        SELECT 
            r.*,
            ARRAY_AGG(STRUCT(
                n.name,
                n.boundaries,
                n.avg_ttv_usd,
                n.retailer_density,
                n.avg_order_frequency,
                n.total_revenue_usd
            )) as neighborhoods
        FROM retailer_metrics r
        LEFT JOIN {self._neighborhoods_table} n
        ON r.city = n.city
        GROUP BY r.city, r.total_revenue_usd, r.total_retailers, r.avg_ttv_usd
        """

        params = [ScalarQueryParameter("city", "STRING", city_name)]
        return await self.execute_query(query, params)

    async def get_neighborhood_metrics(
        self, city_name: str, neighborhood_name: str
    ) -> Dict:
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

        query = f"""
        WITH retailer_metrics AS (
            {self.get_base_retailer_query()}
            WHERE Shipping_City = @city
            GROUP BY 
                Seller_ID, 
                Seller_Name, 
                Store_Name,
                Internal_Seller_Latitude, 
                Internal_Seller_Longitude
        )
        SELECT 
            n.name,
            n.boundaries,
            AVG(r.gross_ttv_usd) as avg_ttv_usd,
            COUNT(DISTINCT r.seller_id) as retailer_density,
            AVG(r.total_orders) as avg_order_frequency,
            SUM(r.revenue_usd) as total_revenue_usd,
            ARRAY_AGG(
                STRUCT(
                    r.seller_id,
                    r.seller_name,
                    r.store_name,
                    r.internal_seller_latitude,
                    r.internal_seller_longitude,
                    r.gross_ttv_usd,
                    r.revenue_usd,
                    r.total_orders,
                    r.product_categories
                )
            ) as retailers
        FROM {self._neighborhoods_table} n
        LEFT JOIN retailer_metrics r
        ON ST_CONTAINS(
            n.boundaries, 
            ST_POINT(r.internal_seller_longitude, r.internal_seller_latitude)
        )
        WHERE n.city = @city 
        AND n.name = @neighborhood
        GROUP BY n.name, n.boundaries
        """

        params = [
            ScalarQueryParameter("city", "STRING", city_name),
            ScalarQueryParameter("neighborhood", "STRING", neighborhood_name),
        ]
        return await self.execute_query(query, params)

    async def get_retailer_metrics(self, seller_id: int) -> Dict:
        """
        Get detailed metrics for a specific retailer.

        Args:
            seller_id (int): The unique identifier of the seller/retailer

        Returns:
            Dict: Retailer metrics including revenue, orders, and location data

        Note:
            Results are cached to improve performance
        """

        query = f"""
        {self.get_base_retailer_query()}
        WHERE Seller_ID = @seller_id
        GROUP BY 
            Seller_ID, 
            Seller_Name, 
            Store_Name,
            Internal_Seller_Latitude, 
            Internal_Seller_Longitude
        """

        params = [ScalarQueryParameter("seller_id", "INT64", seller_id)]
        return await self.execute_query(query, params)

    async def search_retailers(
        self, search_query: str, city: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for retailers based on a query string and optional city filter.

        Args:
            search_query (str): The search query string
            city (Optional[str]): Optional city filter

        Returns:
            List[Dict]: List of retailers matching the search criteria
        """

        query = f"""
        {self.get_base_retailer_query()}
        WHERE LOWER(Store_Name) LIKE LOWER(@query)
        """

        if city:
            query += " AND Shipping_City = @city"

        query += """
        GROUP BY 
            Seller_ID, 
            Seller_Name, 
            Store_Name,
            Internal_Seller_Latitude, 
            Internal_Seller_Longitude
        LIMIT 100
        """

        params = [ScalarQueryParameter("query", "STRING", f"%{search_query}%")]
        if city:
            params.append(ScalarQueryParameter("city", "STRING", city))

        return await self.execute_query(query, params)


# Create a singleton instance
bigquery_client = BigQueryClient()
